import os
import re
import subprocess
import argparse
from bs4 import BeautifulSoup

def run_veracode_scan(scan_type, source, output_file="scan_output.txt"):
    """Runs the Veracode scan command and saves the output to a file."""
    command = [
        "veracode", "scan",
        "--type", scan_type,
        "--source", source,
        "--format", "table",
        "--output", output_file
    ]
    try:
        # Run the command and capture stdout and stderr
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
        # Check for a non-zero exit code and print errors if encountered
        if result.returncode == 0:
            print("Veracode scan failed with the following error:")
            print(result.stderr)  # Detailed error message from stderr
            return None
        
        return output_file
    
    except FileNotFoundError as e:
        print(f"Error: The Veracode CLI executable was not found: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running Veracode scan: {e}")
        return None

def parse_to_html():
    # Reads the scan output file and converts it to an HTML table.
    severity_colors = {
        "Critical": "bg-pink-500",
        "High": "bg-red-500",
        "Medium": "bg-orange-500",
        "Low": "bg-yellow-500",
    }
    
    # Count occurrences of each severity
    severity_count = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }
    
    # Process the file and convert to HTML
    with open("scan_output.txt", "r") as f:
        lines = f.readlines()
    
    # Join lines into a single string
    lines_string = ''.join(lines)

    # Regular expression to find "Vulnerabilities" section up until the next header
    pattern = r"Vulnerabilities\n(.*?)(\n{2,}|No misconfigurations found|No secrets found|Policy Results)"

    # Search for the section
    match = re.search(pattern, lines_string, re.DOTALL)
    if match:
        vulnerabilities = match.group(1).strip().split("\n")
    else:
        print("Vulnerabilities section not found.")
        return None

    # Start the HTML document with head, including Bootstrap CSS and JS links
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com?plugins=forms,typography,aspect-ratio,line-clamp,container-queries"></script>
</head>
<body class="bg-white-100">

  <!-- Title and Subtitle -->
  <div class="px-4 sm:px-8 mt-8">
    <h1 class="text-3xl font-bold text-gray-700">Incident Dashboard</h1>
    <p class="text-gray-500 mt-2">Overview of all incidents and their current status</p>
  </div>

  <!-- Summary Section -->
  <div class="grid grid-cols-1 gap-4 px-4 mt-8 sm:grid-cols-4 sm:px-8">
    <div class="flex items-center bg-white border rounded-sm overflow-hidden shadow">
      <div class="p-4 bg-pink-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7"></path>
        </svg>
      </div>
      <div class="px-4 text-gray-700">
        <h3 class="text-sm tracking-wider">Critical</h3>
        <p class="text-3xl">{}</p>
      </div>
    </div>
    <div class="flex items-center bg-white border rounded-sm overflow-hidden shadow">
      <div class="p-4 bg-red-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6"></path>
        </svg>
      </div>
      <div class="px-4 text-gray-700">
        <h3 class="text-sm tracking-wider">High</h3>
        <p class="text-3xl">{}</p>
      </div>
    </div>
    <div class="flex items-center bg-white border rounded-sm overflow-hidden shadow">
      <div class="p-4 bg-orange-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7a4 4 0 01-8 0"></path>
        </svg>
      </div>
      <div class="px-4 text-gray-700">
        <h3 class="text-sm tracking-wider">Medium</h3>
        <p class="text-3xl">{}</p>
      </div>
    </div>
    <div class="flex items-center bg-white border rounded-sm overflow-hidden shadow">
      <div class="p-4 bg-yellow-500">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292"></path>
        </svg>
      </div>
      <div class="px-4 text-gray-700">
        <h3 class="text-sm tracking-wider">Low</h3>
        <p class="text-3xl">{}</p>
      </div>
    </div>
  </div>

  <!-- Table Section -->
  <div class="shadow-lg rounded-lg overflow-hidden mx-4 md:mx-10 mt-8 bg-white">
    <table class="w-full table-fixed">
        <thead>
            <tr class="bg-gray-100">
    """

    # Add table headers
    headers = vulnerabilities[0].split()
    html += "".join(f"<th class=\"w-1/6 py-3 px-6 text-left text-gray-600 font-bold uppercase\">{header}</th>" for header in headers) + "</tr>\n"
    
    # Close the headers
    html += """
            </thead>
             <tbody class="bg-white">
    """
    
    # Process each row
    for row in vulnerabilities[1:]:
        columns = row.split(maxsplit=len(headers) - 1) 

        # Ensure each column has a default value if missing
        name = columns[0] 
        installed = columns[1]
        fixed_in = columns[2] if len(columns) > 5 else ""
        type_column = columns[3] if len(columns) > 5 else columns[2]
        vulnerability = columns[4] if len(columns) > 5 else columns[3]
        severity = columns[-1].strip()

        # Increment severity count
        if severity in severity_count:
            severity_count[severity] += 1
            
        # Get the color for severity
        color = severity_colors.get(severity, "black") 
        
        html += "<tr>"
        html += f"""<td class="py-3 px-6 border-b border-gray-200">{name}</td>
                    <td class="py-3 px-6 border-b border-gray-200">{installed}</td>
                    <td class="py-3 px-6 border-b border-gray-200">{fixed_in}</td>
                    <td class="py-3 px-6 border-b border-gray-200">{type_column}</td>
                    <td class="py-3 px-6 border-b border-gray-200"><a href="https://vulners.com/osv/OSV:{vulnerability.upper()}" class="font-medium text-blue-600 hover:underline">{vulnerability.upper()}</a></td>
                    <td class="py-3 px-6 border-b border-gray-200">
                        <span class="{color} text-white inline-block text-center px-2 py-1 rounded text-md font-semibold">{severity}</span>
                    </td>
                """
        html += "</tr>\n"
    
    # Close the table and div
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="mt-8">
        </div>
    </body>
    </html>
    """
    
    html = html.format(severity_count["Critical"], severity_count["High"], severity_count["Medium"], severity_count["Low"])
    
    # Beautify HTML for readability using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    pretty_html = soup.prettify()
    return pretty_html

def save_html(html_content, output_file="vulnerabilities_report.html"):
    """Saves the HTML content to an output file."""
    with open(output_file, "w") as f:
        f.write(html_content)
    print(f"HTML report saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Run Veracode scan and convert output to HTML.")
    parser.add_argument("--type", help="Type of scan (e.g., archive, file, folder)")
    parser.add_argument("--source", help="Source file or folder for the scan")
    parser.add_argument("-o", "--output", default="scan_output.txt", help="Temporary output file for scan result")

    args = parser.parse_args()

    # Run Veracode scan and get the output file path
    output_file = run_veracode_scan(args.type, args.source, args.output)
    if not output_file:
        print("Failed to run Veracode scan.")
        return

    # Parse output file to HTML
    html_content = parse_to_html()

    # Save HTML content to a file
    save_html(html_content)

    # Delete temporary output file
    # os.remove(output_file)

if __name__ == "__main__":
    main()
