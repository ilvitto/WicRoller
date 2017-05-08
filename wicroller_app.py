from kivy.app import App
from wicroller import WicRoller

class WicRollerApp_Debug(App):
    def build(self):
        self.load_kv('standard_interface.kv')
        return WicRoller()
        
class WicRollerAppSlider2Mod(App):
    def build(self):
        self.load_kv('slider_interface_2_mod.kv')
        return WicRoller() 
        
class WicRollerApp_Demo_Mute(App):
    def build(self):
        self.load_kv('slider_interface_2_mod_mute.kv')
        return WicRoller() 