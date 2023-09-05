# Libraries
from tqdm import tqdm
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Custom Progress Bar Class
class CustomTqdm(tqdm):
    def update(self, n=1):
        super().update(n)
        if self.n == self.total:
            self.set_description(Fore.GREEN + "DONE" + Fore.RESET, refresh=True) 
            self.set_postfix() 
        else:
            self.set_description(Fore.RED + "LOADING" + Fore.RESET, refresh=True) 
            self.set_postfix()  