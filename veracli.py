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
        "Critical": "darkred",
        "High": "red",
        "Medium": "orange",
        "Low": "green",
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
        <title>Vulnerabilities Report</title>
        <!-- Bootstrap CSS -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <!-- Bootstrap Bundle with Popper JS -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body>
        <div class="container mt-3">
            <h2>Summary</h2>
            <div class="mb-3">
                <span class="badge" style="font-size: 1.5rem; padding: 0.5rem 1rem; background-color: darkred; color: white;">Critical: {}</span>
                <span class="badge" style="font-size: 1.5rem; padding: 0.5rem 1rem; background-color: red; color: white;">High: {}</span>
                <span class="badge" style="font-size: 1.5rem; padding: 0.5rem 1rem; background-color: orange; color: black;">Medium: {}</span>
                <span class="badge" style="font-size: 1.5rem; padding: 0.5rem 1rem; background-color: green; color: white;">Low: {}</span>
            </div>
            
            <h2>Vulnerabilities</h2>
            <table class="table table-bordered">
                <thead class="table-light">
                    <tr>
    """

    # Add table headers
    headers = vulnerabilities[0].split()
    html += "".join(f"<th>{header}</th>" for header in headers) + "</tr>\n"
    
    # Close the headers
    html += """
            </thead>
            <tbody>
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
        html += f"""<td>{name}</td>
                    <td>{installed}</td>
                    <td>{fixed_in}</td>
                    <td>{type_column}</td>
                    <td><a href="https://vulners.com/osv/OSV:{vulnerability.upper()}">{vulnerability.upper()}</a></td>
                    <td class="fw-bolder" style='color:{color};'>{severity}</td>
                """
        html += "</tr>\n"
    
    # Close the table and div
    html += """
                </tbody>
            </table>
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
    os.remove(output_file)

if __name__ == "__main__":
    main()