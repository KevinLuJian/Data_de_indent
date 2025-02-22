import xml.etree.ElementTree as ET
import ollama
import argparse
import os
import re

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

    Wrap the de-identified patient history with <text></text> tags.

    Patient Name: {Patient_name}
    non-deindentified patient history:
    {history_text.strip()}
    deindentified patient history:
    '''
    model = 'internlm2:20b'
   
    
    pattern = re.compile(r'<text>(.*?)</text>', re.DOTALL)

    while True:
        response = ollama.generate(model=model, prompt=Prompt)
        answer = response['response']
        match = pattern.search(answer)
        if match is None:
            continue
        deindentified_text = match.group(1)
        if len(deindentified_text) == 0:
            continue
        
        return deindentified_text

def checking_LLM(original, deindentified):
    # # Check if the de-identified text is correct
    # print("Original text:", original)
    # print("De-identified text:", deindentified)
    # print("Is the de-identified text correct? (yes/no)")
    Prompt = f'''
    Task: Text Verification and De-identification Consistency
    You are an expert in text verification and de-identification consistency. Your task is to compare the original text with the de-identified text and determine whether they convey the same meaning.

    Key De-identification Rules:

    Specific months and days are replaced with xxxx, years information is acceptable and can be preserved.
    Patient names are replaced with XXXXXXXX.
    These replacements are expected and acceptable.
    Aside from these modifications, the two texts should be nearly identical. Your goal is to check if the de-identified text deviates too much from the original.

    Original text: 
    {original}

    De-identified text: 
    {deindentified}

    You answer should be one of the following:
    A. Match
    B. Mismatch
    End your response with:
    My answer is ... (followed by A or B)
    '''
    model = 'llama3.1'
   
    
    pattern = r"My answer is (.*)"

    while True:
        response = ollama.generate(model=model, prompt=Prompt)
        answer = response['response']
        match = re.search(pattern, answer)
        if match is None:
            continue
        option = match.group(1)
        print(answer)
        print("option:", option)
        
        return option
    '''
    Task: Text Verification and De-identification Consistency
    You are an expert in text verification and de-identification consistency. Your task is to compare the original text with the de-identified text and determine whether they convey the same meaning.

    Key De-identification Rules:

    Specific months and days are replaced with xxxx, years information is acceptable and can be preserved.
    Patient names are replaced with XXXXXXXX.
    These replacements are expected and acceptable.
    Aside from these modifications, the two texts should be nearly identical. Your goal is to check if the de-identified text deviates too much from the original.

    Original text: 
    Medications: cyclobenzaprine 10 mg TID PRN”

    De-identified text: 
    XXXXX was diagnosed with hypertension on October 1, 2019. He began taking lisinopril 5 mg daily to manage his blood pressure. The patient has shown good compliance with the medication regimen and has maintained stable blood pressure readings throughout the year. His most recent lab results indicate normal renal function.
    
    You answer should be one of the following:
    A. Match
    B. Mismatch
    End your response with:
    My answer is ... (followed by A or B)
    '''

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
    print("Patient name:", Patient_name)
    history_text = ""
    for text_elem in root.findall(".//EMGData[@name='Patient History']/EMGtext"):
        if text_elem.text:
            history_text = text_elem.text.strip() + " "
            while True:
                text = LLM_processing(Patient_name, history_text)
                text_elem.text = text
                print(f"Original report: \n {history_text}")
                print(f"De-identified report: {text}")
                print("=====================================")
                print("Checking the de-identified text....")
                answer = checking_LLM(history_text, text)
                if 'A' in answer:
                    print("The de-identified text is matched.")
                    break
                else:
                    print("The de-identified text is mismatched, try again.")
            


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