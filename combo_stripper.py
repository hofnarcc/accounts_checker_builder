import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from threading import Thread

def preprocess_file(input_file, intermediate_file, progress, log):
    with open(input_file, 'r', encoding='utf-8') as infile, open(intermediate_file, 'w', encoding='utf-8') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)
        for line_number, line in enumerate(infile, 1):
            parts = line.split(':')
            if len(parts) > 2:
                user_pass = ':'.join(parts[-2:])  # Take the last two parts as user:pass
                url_part = ':'.join(parts[:-2])   # Take the rest as URL
                outfile.write(f"{url_part.strip()} {user_pass.strip()}\n")
            else:
                outfile.write(line)
            
            if line_number % 1000 == 0:
                progress['value'] = (line_number / total_lines) * 100
                log.insert(tk.END, f"Preprocessed {line_number} lines...\n")
                log.yview(tk.END)
                root.update_idletasks()
        
    progress['value'] = 100
    log.insert(tk.END, "Preprocessing complete. Intermediate data written to: {}\n".format(intermediate_file))
    log.yview(tk.END)

def remove_urls_from_file(input_file, intermediate_cleaned_file, progress, log):
    url_pattern = re.compile(
        r'\bhttps?://(?:www\.)?[a-zA-Z0-9\-._~:/?#@!$&\'()*+,;=]+(?:\.[a-zA-Z]{2,})?\b'
    )

    with open(input_file, 'r', encoding='utf-8') as infile, open(intermediate_cleaned_file, 'w', encoding='utf-8') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)
        for line_number, line in enumerate(infile, 1):
            parts = line.split()
            cleaned_parts = [url_pattern.sub('', part) if url_pattern.match(part) else part for part in parts]
            cleaned_line = ' '.join(cleaned_parts)
            outfile.write(cleaned_line + '\n')
            
            if line_number % 1000 == 0:
                progress['value'] = (line_number / total_lines) * 100
                log.insert(tk.END, f"Processed {line_number} lines...\n")
                log.yview(tk.END)
                root.update_idletasks()
        
    progress['value'] = 100
    log.insert(tk.END, "URL removal complete. Intermediate cleaned data written to: {}\n".format(intermediate_cleaned_file))
    log.yview(tk.END)

def final_clean_file(input_file, final_output_file, progress, log):
    os_patterns = re.compile(r'\b(?:windows|android|linux|mac|ios|unix|ubuntu):\/\/', re.IGNORECASE)

    with open(input_file, 'r', encoding='utf-8') as infile, open(final_output_file, 'w', encoding='utf-8') as outfile:
        total_lines = sum(1 for _ in infile)
        infile.seek(0)
        for line_number, line in enumerate(infile, 1):
            parts = line.split()
            for part in parts:
                if ':' in part and not os_patterns.search(part):
                    user_pass_parts = part.split(':')
                    if len(user_pass_parts) == 2:
                        outfile.write(part + '\n')
                        break  # Exit after writing the first valid user:pass pair
            
            if line_number % 1000 == 0:
                progress['value'] = (line_number / total_lines) * 100
                log.insert(tk.END, f"Final cleaned {line_number} lines...\n")
                log.yview(tk.END)
                root.update_idletasks()
        
    progress['value'] = 100
    log.insert(tk.END, "Final cleaning complete. Cleaned data written to: {}\n".format(final_output_file))
    log.yview(tk.END)

def generate_intermediate_file_name(input_file):
    base_name, ext = os.path.splitext(input_file)
    return f"{base_name}-intermediate{ext}"

def generate_intermediate_cleaned_file_name(intermediate_file):
    base_name, ext = os.path.splitext(intermediate_file)
    return f"{base_name}-intermediate-cleaned{ext}"

def generate_final_file_name(output_dir, output_filename):
    return os.path.join(output_dir, output_filename)

def run_process(input_file, output_dir, output_filename, progress, log, start_button):
    try:
        start_button.config(text="Processing...", state=tk.DISABLED)
        intermediate_file_path = generate_intermediate_file_name(input_file)
        intermediate_cleaned_file_path = generate_intermediate_cleaned_file_name(intermediate_file_path)
        final_output_file_path = generate_final_file_name(output_dir, output_filename)

        log.insert(tk.END, "Starting preprocessing step...\n")
        preprocess_file(input_file, intermediate_file_path, progress, log)

        log.insert(tk.END, "Starting URL removal step...\n")
        remove_urls_from_file(intermediate_file_path, intermediate_cleaned_file_path, progress, log)

        log.insert(tk.END, "Starting final cleaning step...\n")
        final_clean_file(intermediate_cleaned_file_path, final_output_file_path, progress, log)

        messagebox.showinfo("Success", f"All steps completed successfully! Final file: {final_output_file_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        start_button.config(text="Start Processing", state=tk.NORMAL)

def select_file():
    file_path = filedialog.askopenfilename(title="Select Input File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if file_path:
        input_file_label.config(text=file_path)
        app.input_file = file_path

def select_output_dir():
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if output_dir:
        output_dir_label.config(text=output_dir)
        app.output_dir = output_dir

def start_processing():
    if hasattr(app, 'input_file') and hasattr(app, 'output_dir') and output_filename.get():
        progress['value'] = 0
        log.delete(1.0, tk.END)
        Thread(target=run_process, args=(app.input_file, app.output_dir, output_filename.get(), progress, log, start_button)).start()
    else:
        messagebox.showwarning("Warning", "Please select an input file, an output directory, and specify an output filename")

def toggle_log():
    if log_frame.winfo_viewable():
        log_frame.grid_remove()
        toggle_log_button.config(text="Show Log")
    else:
        log_frame.grid()
        toggle_log_button.config(text="Hide Log")

# Create the main window
root = tk.Tk()
root.title("Data Processing")

app = tk.Frame(root)
app.pack(padx=10, pady=10)

# Add a button to select the input file
select_file_button = tk.Button(app, text="Select Input File", command=select_file)
select_file_button.grid(row=0, column=0, pady=(0, 10))

# Add a label to display the selected input file
input_file_label = tk.Label(app, text="No file selected")
input_file_label.grid(row=0, column=1, pady=(0, 10), padx=(10, 0))

# Add a button to select the output directory
select_output_dir_button = tk.Button(app, text="Select Output Directory", command=select_output_dir)
select_output_dir_button.grid(row=1, column=0, pady=(0, 10))

# Add a label to display the selected output directory
output_dir_label = tk.Label(app, text="No directory selected")
output_dir_label.grid(row=1, column=1, pady=(0, 10), padx=(10, 0))

# Add a label and entry for the output filename
output_filename_label = tk.Label(app, text="Output Filename:")
output_filename_label.grid(row=2, column=0, pady=(0, 10))

output_filename = tk.Entry(app)
output_filename.grid(row=2, column=1, pady=(0, 10), padx=(10, 0))

# Add a progress bar
progress = ttk.Progressbar(app, orient="horizontal", length=300, mode="determinate", style="green.Horizontal.TProgressbar")
progress.grid(row=3, column=0, columnspan=2, pady=(10, 0))

# Add a button to start the processing
start_button = tk.Button(app, text="Start Processing", command=start_processing)
start_button.grid(row=4, column=0, columnspan=2, pady=(10, 0))

# Add a button to toggle the log area
toggle_log_button = tk.Button(app, text="Show Log", command=toggle_log)
toggle_log_button.grid(row=5, column=0, columnspan=2, pady=(10, 0))

# Add a frame for the log area
log_frame = tk.Frame(app)
log_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="nsew")
log_frame.grid_remove()

# Add a text widget for logging
log = tk.Text(log_frame, height=10, width=60)
log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a scrollbar for the log area
scrollbar = tk.Scrollbar(log_frame, command=log.yview)
log.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the progress bar style
style = ttk.Style(root)
style.configure("green.Horizontal.TProgressbar", foreground='green', background='green')

# Run the GUI main loop
root.mainloop()
