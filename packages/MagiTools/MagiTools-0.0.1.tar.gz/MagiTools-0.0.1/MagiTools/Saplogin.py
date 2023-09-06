import win32com.client
import subprocess
import time

class SapGui():
    def __init__(self,pathSap,type):

        try:
            self.path = f"{pathSap}"
            subprocess.Popen([self.path])
            time.sleep(6)
            self.SapGuiAuto = win32com.client.GetObject("SAPGUI")
            application = self.SapGuiAuto.GetScriptingEngine
            self.connection = application.OpenConnection(f"{type}",True)
            session = self.connection.Children(0)
            self.session = session
            
        except Exception as e:
            print(e)
        
    def login(self,user,password,mandante):
        session = self.session
        session.findById('wnd[0]').maximize
        session.findById("wnd[0]/usr/txtRSYST-MANDT").text = f"{mandante}"
        session.findById("wnd[0]/usr/txtRSYST-BNAME").text = f"{user}"
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").text = f"{password}"
        session.findById("wnd[0]/usr/txtRSYST-LANGU").text = "PT"
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").setFocus
        session.findById("wnd[0]/usr/pwdRSYST-BCODE").caretPosition = 12
        session.findById("wnd[0]/tbar[0]/btn[0]").press
        session.findById("wnd[0]").sendVKey(0)

    def transacao(self,transacao):
        session = self.session
        session.findById("wnd[0]/tbar[0]/okcd").text = f"/n{transacao}"
        session.findById("wnd[0]/tbar[0]/btn[0]").press
        session.findById("wnd[0]").sendVKey(0)

    def Scripts(self,scripts):
        session = self.session
        print(type(session))
        script_lines = scripts.split('\n')

        for line in script_lines:
            try:
                # Remove espaços em branco no início e no final de cada linha
                line = line.strip()
                
                # Verifica se a linha não está vazia
                if line:
                    # Execute a linha como um comando
                    exec(line)
            except Exception as e:
                print(f"Error executing line: {e}")

    def logoff(self):
        session = self.session
        try:
            session.findById("wnd[0]").Close()  # Fecha a janela principal do SAP
            session.findById("wnd[1]/usr/btnSPOP-OPTION1").press
        except Exception as e:
            print(f"Error closing SAP: {e}")
        
        
        


            
   




