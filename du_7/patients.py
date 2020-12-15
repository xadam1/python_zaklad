'''
Opravte chyby v tomto programu.

Zadání: 
Spočítej a vypiš body mass index (BMI = (hmotnost v kg) / (výška v m)**2) všech pacientů ze seznamu patients.
U pacientů s BMI mimo normální rozsah (18.5–25) vypiš vykřičník.
Nakonec vypiš průměr a median BMI.

Očekávaný výstup:
Bob's BMI is: 27.7 !
Alice's BMI is: 21.8 
Cyril's BMI is: 22.8 
-----------------
Average BMI: 24.1
Median BMI:  22.8
'''
import statistics

BMI_OK_RANGE = (18.5, 25)  # Bezpečný rozsah BMI


def calculate_bmi(weight: float, height: float) -> float:
    '''Spočítej BMI pacienta o hmotnosti weight (kg) a výšce height (m).'''
    return weight / (height ** 2)


def is_bmi_ok(bmi: float) -> bool:
    '''Rozhodni jestli je BMI v bezpečném rozsahu.'''
    return (bmi >= BMI_OK_RANGE[0]) and (bmi <= BMI_OK_RANGE[1])


def main() -> None:
    # Jméno, hmotnost a výška jednotlivých pacientů
    patients = [('Bob', 80, 1.7), ('Alice', 64.5, 1.72), ('Cyril', 74, 1.8)]
    bmis = []
    for patient in patients:
        (name, weight, height) = patient
        bmi = calculate_bmi(weight, height)
        bmis.append(bmi)
        if not is_bmi_ok(bmi):
            warning = '!'
        else:
            warning = ''
        print(f'{name}\'s BMI is: {bmi:.1f} {warning}')
    average = sum(bmis) / len(bmis)
    median = statistics.median(bmis)
    print('-----------------')
    print(f'Average BMI: {average:.1f}')
    print(f'Median BMI:  {median:.1f}')


if __name__ == '__main__':
    main()
