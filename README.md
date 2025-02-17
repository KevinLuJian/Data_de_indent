# Data_De_Indent

This repository contains a script for information de-identification.

### Data Fields to Be Removed:
**<Exam>:**
- Visit Number  
- Exam Date  
- Signed on  
- Billed on  
- Uploaded on  
- OrderID  

**<Patient>:**  
- PID  
- First Name  
- Last Name  
- DOB  
- Phone  

**<Patient History>**
The name of the patient is being replaced as xxxxxx, and all the date, except year, has also been removed.

> **Note:** The `Raw_data` folder in this repository contains randomly generated personal information for testing purposes only.

---

### Usage

To run the code, use the following command:

```bash
python de_indent.py --target Raw_data --de_indent de_indent 

```

This command will automatically convert all files in Raw_data to de-identified files saved in the de_indent folder.


The automatic de-identification of patient history utilizes the open-source software Ollama. Please download Ollama first.

After installing Ollama, install the required LLM by running the following command in the terminal:

```bash
pip install ollama
ollama run internlm2:20
```

In this script, we use internlm2:20, which requires approximately 14 GB of graphics memory.
