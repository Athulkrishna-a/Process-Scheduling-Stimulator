import wx
import threading
import time
from queue import PriorityQueue

class Process:
    def __init__(self, name, priority, execution_time):
        self.name = name
        self.priority = priority
        self.execution_time = execution_time

    def __lt__(self, other):
        if scheduling_algorithm == "Priority":
            return self.priority < other.priority
        elif scheduling_algorithm == "SJF":
            return self.execution_time < other.execution_time

class ProcessScheduler(wx.Frame):
    def __init__(self, parent, title):
        super(ProcessScheduler, self).__init__(parent, title=title, size=(500, 400))

        self.process_queue = PriorityQueue()
        self.current_process = None
        self.execution_thread = None
        self.start_time = None

        self.panel = wx.Panel(self)

        # Set background color to accent green
        self.panel.SetBackgroundColour(wx.Colour(215, 247, 173 ))

        # Create a font with medium size and italic style
        title_font = wx.Font(wx.FontInfo(16).Bold().Italic())

        # Create a static text for the title
        self.title_label = wx.StaticText(self.panel, label="Process Scheduling Stimulator ⏳🎚️", style=wx.ALIGN_CENTER)
        self.title_label.SetFont(title_font)

        self.process_list = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.process_list.InsertColumn(0, "Process Name", width=150)
        self.process_list.InsertColumn(1, "Priority", width=100)
        self.process_list.InsertColumn(2, "Execution Time", width=100)
        self.process_list.InsertColumn(3, "Status", width=100)

        self.algorithm_choice = wx.Choice(self.panel, choices=["Priority", "SJF"])
        self.algorithm_choice.Bind(wx.EVT_CHOICE, self.on_algorithm_choice)

        self.add_button = wx.Button(self.panel, label="Add Process")
        self.add_button.Bind(wx.EVT_BUTTON, self.on_add_process)

        self.start_button = wx.Button(self.panel, label="Start Execution")
        self.start_button.Bind(wx.EVT_BUTTON, self.on_start_execution)

        self.queue_label = wx.StaticText(self.panel, label="Process Queue:")
        self.algorithm_label = wx.StaticText(self.panel, label="Scheduling Algorithm:")

        self.layout = wx.BoxSizer(wx.VERTICAL)
        
        # Add the title label to the layout
        self.layout.Add(self.title_label, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        self.layout.Add(self.algorithm_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.layout.Add(self.algorithm_choice, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.layout.Add(self.process_list, 1, wx.EXPAND | wx.ALL, 5)
        self.layout.Add(self.add_button, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.layout.Add(self.start_button, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        self.layout.Add(self.queue_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)

        self.panel.SetSizer(self.layout)

        self.process_count = 0  # Initialize the process count

        self.Centre()
        self.Show()

    def on_algorithm_choice(self, event):
        global scheduling_algorithm
        selected_algorithm = self.algorithm_choice.GetStringSelection()
        scheduling_algorithm = selected_algorithm

    def on_add_process(self, event):
        dlg = wx.TextEntryDialog(self, "Enter Process Name, Priority, and Execution Time (comma-separated):", "Add Process")
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetValue().split(',')
            if len(data) == 3:
                name, priority, execution_time = data
                process = Process(name.strip(), int(priority.strip()), int(execution_time.strip()))
                self.process_queue.put(process)
                self.process_count += 1
                self.update_process_list()
        dlg.Destroy()

    def on_start_execution(self, event):
        if not self.current_process and not self.process_queue.empty():
            self.current_process = self.process_queue.get()
            self.start_time = time.time()  # Start measuring execution time
            self.update_process_list()

            # Start execution in a separate thread
            self.execution_thread = threading.Thread(target=self.execute_process, args=(self.current_process,))
            self.execution_thread.start()

    def execute_process(self, process):
        if process:
            self.process_list.SetStringItem(self.process_count - 1, 3, "Executing")
            time.sleep(process.execution_time)  # Simulate process execution time
            execution_time = time.time() - self.start_time  # Calculate execution time
            self.process_list.SetStringItem(self.process_count - 1, 3, "Completed")
            self.show_completion_message(process.name, execution_time)  # Show pop-up message
            self.current_process = None
            self.process_count -= 1  # Decrement the process count
            self.update_process_list()

            # Automatically start the next process if the queue is not empty
            if not self.process_queue.empty():
                self.on_start_execution(None)

    def show_completion_message(self, process_name, execution_time):
        dlg = wx.MessageDialog(self, f"{process_name} Completed in {execution_time:.2f} seconds",
                               "Process Completed", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def update_process_list(self):
        self.process_list.DeleteAllItems()
        for i, process in enumerate(list(self.process_queue.queue)):
            self.process_list.InsertItem(i, process.name)
            self.process_list.SetItem(i, 1, str(process.priority))
            self.process_list.SetItem(i, 2, str(process.execution_time))
            self.process_list.SetItem(i, 3, "Waiting")

        if self.current_process:
            self.process_list.InsertItem(self.process_count - 1, self.current_process.name)
            self.process_list.SetItem(self.process_count - 1, 1, str(self.current_process.priority))
            self.process_list.SetItem(self.process_count - 1, 2, str(self.current_process.execution_time))
            self.process_list.SetItem(self.process_count - 1, 3, "Executing")

        if self.process_queue.empty() and not self.current_process:
            self.queue_label.SetLabel("Process Queue: (Empty)")

if __name__ == '__main__':
    app = wx.App()
    scheduling_algorithm = "Priority"  # Default scheduling algorithm
    ProcessScheduler(None, title='Process Scheduler')
    app.MainLoop()
