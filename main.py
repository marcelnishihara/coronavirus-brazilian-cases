import json

colors = {
    "err" : "\033[91m",
    "end" : "\033[m",
    "success" : "\033[92m",
    "warning" : "\033[93m"
}


def main(request):
    with open('sao_carlos_cases.json', 'r') as sao_carlos_cases:
        cases = sao_carlos_cases.read()
        msg = f"Returning the dictionary of COVID-19 cases in São Carlos, SP, Brazil"
        pretty_print(msg, True)
        return cases


def pretty_print(msg, status):
    if status == True:
        format_msg = f"{colors['success']}{msg}{colors['end']}"
    else :
        format_msg = f"{colors['err']}{msg}{colors['end']}"

    print(format_msg, end="\n\n")
