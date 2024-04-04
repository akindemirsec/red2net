import os
import time
import yaml
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class Red2NetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Red2Net")
        
        self.script_dir = "playbooks"
        self.arguments_file = "playbooks/arguments.yaml"
        
        self.load_scripts()
        
        self.script_var = tk.StringVar(root)
        self.script_var.set(self.scripts[0])
        
        self.create_widgets()
        
    def load_scripts(self):
        self.scripts = [file for file in os.listdir(self.script_dir) if file.endswith((".py", ".c", ".sh"))]
        
    def create_widgets(self):
        self.root.config(bg="#424242")

        tk.Label(self.root, text="Choose a script:", bg="#424242", fg="white").pack()
        self.script_menu = tk.OptionMenu(self.root, self.script_var, *self.scripts)
        self.script_menu.config(bg="#424242", fg="white") 
        self.script_menu.pack()
        
        run_button = tk.Button(self.root, text="Run Script", command=self.run_script, bg="#30120C", fg="white")
        run_button.pack()

        output_label = tk.Label(self.root, text="Terminal Output", bg="#424242", fg="white")
        output_label.pack(anchor="w")
        self.output_text = tk.Text(self.root, height=20, width=80, bg="#050505", fg="white", relief="flat")
        self.output_text.pack(pady=10)

        
    def run_script(self):
        self.output_text.delete(1.0, tk.END)
        
        selected_script = self.script_var.get()
        self.output_text.insert(tk.END, f"{selected_script} starting...\n\n") 
        
        arguments = self.load_arguments(selected_script)
        if not arguments:
            messagebox.showerror("Error", "Arguments file not found for the selected script.")
            return
        
        params = self.get_parameters(arguments)
        if not params:
            return
        
        script_path = os.path.join(self.script_dir, selected_script)
        command = []
        if selected_script.endswith((".sh", ".c")):
            command.extend(["sudo", "./" + selected_script]) 
        else:
            command.extend(["sudo", "python", script_path])
        
        for arg, value in params.items():
            command.extend(["-" + arg, value])
        
        self.output_text.insert(tk.END, "$ " + " ".join(command) + "\n\n")
        
        try:
            output = subprocess.run(command, capture_output=True, text=True, check=True, cwd=self.script_dir, env={"PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"})
            self.output_text.insert(tk.END, output.stdout)
        except subprocess.CalledProcessError as e:
            self.output_text.insert(tk.END, f"Error: {e.stderr}\n")



 
    def load_arguments(self, script_name):
        arguments_file = os.path.join(self.script_dir, "arguments.yaml")
        if os.path.exists(arguments_file):
            with open(arguments_file, "r") as f:
                arguments = yaml.safe_load(f)
            if script_name in arguments:
                return arguments[script_name]
        return None
    
    def get_parameters(self, arguments):
        params = {}
        dialog = ArgumentDialog(self.root, arguments)
        self.root.wait_window(dialog.top)
        if dialog.result is None:
            return None
        else:
            return dialog.result

class ArgumentDialog:
    def __init__(self, parent, arguments):
        self.parent = parent
        self.arguments = arguments
        
        self.top = tk.Toplevel(parent)
        self.top.title("Enter Arguments")
        self.top.config(bg="#424242")
        
        self.entries = {}
        
        for i, arg in enumerate(arguments):
            label = tk.Label(self.top, text=arg, bg="#424242", fg="white")  
            label.grid(row=i, column=0, padx=10, pady=5, sticky="w")  
            entry = tk.Entry(self.top)
            entry.config(bg="white", fg="#333") 
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="e")  
            self.entries[arg] = entry
        
        ok_button = tk.Button(self.top, text="OK", command=self.ok, bg="#30120C", fg="white")
        ok_button.grid(row=len(arguments), column=0, columnspan=2, padx=10, pady=10) 
        cancel_button = tk.Button(self.top, text="Cancel", command=self.cancel, bg="#30120C", fg="white")
        cancel_button.grid(row=len(arguments) + 1, column=0, columnspan=2, padx=10, pady=5) 
        
        self.result = None

    def ok(self):
        self.result = {arg: entry.get() for arg, entry in self.entries.items()}
        self.top.destroy()
        
    def cancel(self):
        self.result = None
        self.top.destroy()

def show_ascii_art():
    art_file = os.path.join("utils", "ascii_art.txt")
    if os.path.exists(art_file):
        with open(art_file, "r") as f:
            ascii_art = f.read()
        print(ascii_art)
        time.sleep(3)
        subprocess.call("clear" if os.name == "posix" else "cls", shell=True)  
    else:
        print("ASCII art file not found!")

if __name__ == "__main__":
    
    root = tk.Tk()
    app = Red2NetApp(root)
    root.mainloop()
