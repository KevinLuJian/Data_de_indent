import xml.etree.ElementTree as ET
import ollama
import argparse
import os

## What needs to be deindentified is the following:
### <Exam>:
#     Visit Number
#     Exam Date
#     Signed on
#     Billed on
#     Uploaded on
#     OrderID
# <Patient>:
#     PID
#     First Name
#     Last Name
#     DOB
#     Phone
# <Patient History>

###

def LLM_processing(Patient_name, history_text):
    Prompt = f'''
    You will be provided with a patient history. Your task is to de-identify the patient history by removing all references to the patient's name, including any shortened forms (e.g., Chris for Christopher). Replace all occurrences of the patient's name or its short forms with XXXXXXXX.

    Additionally, remove all date information except the year, which should remain unchanged.

    Do not remove any doctor names or other non-patient-related information. If no de-identification is needed, leave the text unchanged.

    Output only the de-identified patient history without any additional text, headers, or explanations.

    Patient Name: {Patient_name}
    Text:
    {history_text.strip()}
    '''


    model = 'internlm2:20b'
    response = ollama.generate(model=model, prompt=Prompt)
    deindentified_text = response['response']
    maximum = 10 # try to deindentifiy the data 10 times maximum.
    iteration = 0
    while abs(len(deindentified_text) - len(history_text)) > 20:
        print("The de-indentified text is too different from the original text. Trying again....")
        # print("Original text is: ", history_text)
        # print("De-indentified text is: ", deindentified_text)

        response = ollama.generate(model=model, prompt=Prompt)
        deindentified_text = response['response']
        iteration += 1
        if iteration > maximum:
            break

    return deindentified_text

def parse_arguments():
    parser = argparse.ArgumentParser(description='De-identify XML data.')
    parser.add_argument('--target', type=str, required=True, help='Path to the input XML file.')
    parser.add_argument('--de_indent', type=str, required=True, help='Path to save the de-identified XML file.')
    return parser.parse_args()


def de_indent_file(file_path, de_indent_folder):
    tree = ET.parse(file_path)
    root = tree.getroot()
    tree = ET.parse(file_path)
    root = tree.getroot()

    file_name = file_path.split('/')[-1]
    ## Exam: 
    exam = root.find(".//EMGData[@name='Exam']")

    visit_number = exam.find(".//EMGparam[@name='Visit Number']")
    visit_number.set('value', 'XXXXXXXX')  # Change the value

    Exam_date = exam.find(".//EMGparam[@name='Exam Date']")
    year = Exam_date.get('value')[:4]
    print(year)
    Exam_date.set('value',f"{year}-mm-dd hh:MM:ss")

    Signed_on = exam.find(".//EMGparam[@name='Signed On']")
    year = Signed_on.get('value')[:4]
    Signed_on.set('value',f"{year}-mm-dd hh:MM:ss")

    Billed_on = exam.find(".//EMGparam[@name='Billed On']")
    year = Billed_on.get('value')[:4]
    Billed_on.set('value',f"{year}-mm-dd hh:MM:ss")

    Uploaded_on = exam.find(".//EMGparam[@name='Uploaded On']")
    year = Uploaded_on.get('value')[:4]
    Uploaded_on.set('value',f"{year}-mm-dd hh:MM:ss")

    OrderID = exam.find(".//EMGparam[@name='OrderID']")
    OrderID.set('value', 'XXXXXXXX')  # Change the value

    ## Patient:

    patient = root.find(".//EMGData[@name='Patient']")

    PID = patient.find(".//EMGparam[@name='PID']")
    PID.set('value', 'XXXXXXXX')  # Change the value



    First_Name = patient.find(".//EMGparam[@name='First Name']")


    Last_Name = patient.find(".//EMGparam[@name='Last Name']")

    Patient_name = First_Name.get('value') + ' ' + Last_Name.get('value')
    First_Name.set('value', 'XXXXXXXX')
    Last_Name.set('value', 'XXXXXXXX')

    DOB = patient.find(".//EMGparam[@name='DOB']")
    year = DOB.get('value')[:4]
    DOB.set('value',f"{year}-mm-dd hh:MM:ss")

    Phone = patient.find(".//EMGparam[@name='Phone']")
    Phone.set('value', '')



    ## Deal with Patient History
    print("patient name is ", Patient_name)
    # Patient_History = root.find(".//EMGData[@name='Patient History']")
    history_text = ""
    for text_elem in root.findall(".//EMGData[@name='Patient History']/EMGtext"):
        if text_elem.text:
            history_text = text_elem.text.strip() + " "
            text = LLM_processing(Patient_name, history_text)
            text_elem.text = text
            print(f"changing {history_text} \n\n to \n\n{text}")
            print("=====================================")


    # Save to a new folder
    output_path = f'{de_indent_folder}/deindent_{file_name}'
    if not os.path.exists(de_indent_folder):
        os.makedirs(de_indent_folder)

    tree.write(output_path)

    print("Updated XML saved to:", output_path)

def de_indent_folder(target_folder, de_indent_folder):
    for file in sorted(os.listdir(target_folder)):

        if file.endswith(".xml"):

            print(f"De-indentifying {file}.....")
            de_indent_file(f"{target_folder}/{file}", de_indent_folder)
            print("=====================================")


if __name__ == '__main__':
    args = parse_arguments()
    target= args.target
    de_indent = args.de_indent

    de_indent_folder(target, de_indent)


    # de_indent_file(f"{target_folder}/123.xml", de_indent_folder)