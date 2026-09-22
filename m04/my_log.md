## My Lab Notebook for CS1066 PSet #2

PHILIP VAN TONDER

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### Describe Your Decomposition Approach

This problem can broadly be broken into three sub-problems. The first is obtaining the data from some source, in this case the SEC EDGAR database. The second is processing the extracted data. The third is displaying the data. My approach to breaking the specification into smaller problems will follow logically from this general statement.

I will first fetch the data from the SEC database using the SEC EDGAR API. Next, I will extract the revenue, net income and assets from the structured data obtained using the SEC EDGAR API. Finally, the revenue, net income and assets will be plotted and then displayed on a web app. Each sub-problem will be solved using its own python script. This will allow me to check the outputs for each script separately and ensure that working code is not affected by newly generated code.

----
----

### Document Your Iterations with AI

----

Text of my first prompt:

> I want to build a web based financial analysis tool that fetches data from the SEC EDGAR API and displays company revenue, net income and assets over the last 10 years. Keep this context in mind for the following prompts. I will break the problem down into sub-problems, but structure your code for each step with this end goal in mind.

Reflections on success/failure of this prompt:

*   This prompt is only to provide context to the AI about the ultimate goal of the sub-tasks that follow.

----

Text of my next prompt:

> Work in the directory m04. create a python script called sec_data_fetch.py. This script should take a 10 digit CIK number from the user. Next, it should use the CIK number and extract the company facts as a JSON file from the SEC EDGAR databse using the EDGAR API. The script should return company_data.json containing the fetched data.

Reflections on success/failure of this prompt:

*   WRITE-BULLET-LIST-OF-THOUGHTS

----

**NOTE:** Delete this text and repeat the above block for as many prompts as it takes to complete the pset.

----

**FINAL REFLECTION:** Review your prompting work. How does your work on this pset compare with that of the first pset?

... YOUR FINAL REFLECTIONS HERE ...

----
----

### Handling the Problem's Whitespace

When you have a working solution, write a brief statement describing how you ultimately approached the problem's whitespace. What you might have done differently in hindsight, and why? Or defend why your work was a good approach.

... YOUR FINAL REFLECTIONS HERE ...

----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
