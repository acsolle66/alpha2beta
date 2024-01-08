import re
from typing import List, Tuple
from math import pi, sqrt

import customtkinter as ctk
import tkinter.messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class Alpha2BetaApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("alpha2beta")
        self.geometry("390x320")
        self.resizable(False, False)

        self.labels = {
            "descriptions": [" - Tlaková osová sila", " - Dĺžka prvku", " - Modul pružnosti", " - Plocha prvku",
                             " - Moment zotrvačnosti", " - Polomer zotrvačnosti",
                             " - Súčiniteľ kritickej sily"],
            "symbols": ["NEd", "L", "E", "A", "I", "i", "αcrit"],
            "units": ["[ kN ]", "[ m ]", "[ GPa ]", "[ mm² ]", "[ mm⁴ ]", "[ mm ]", "[ - ]"]}
        self.rows = len(self.labels["descriptions"])

        # Registering validators
        numeric_validator = self.register(self.numeric_input_validator)

        self._add_labels_()

        self.variables = [ctk.StringVar(value="0.000", name=self.labels["symbols"][i]) for i in range(0, self.rows)]

        self.entries = [
            ctk.CTkEntry(self, textvariable=variable, validate="all", validatecommand=(numeric_validator, "%P")) for
            variable in self.variables]
        for i in range(0, len(self.entries)):
            self.entries[i].grid(row=i, column=2, padx=(15, 0), pady=(5, 0), sticky="E")

        self.entries[3].configure(fg_color="#a9a9a9", state="disabled")

        self.button_calc = ctk.CTkButton(self, text="Výpočet", command=self.calculate, )
        self.button_calc.grid(row=8, column=0, columnspan=4, pady=(15, 0))

        self.output_label = ctk.CTkLabel(self, text="")
        self.output_label.grid(row=9, columnspan=4, padx=(5, 0), pady=(5, 0))

    def _add_labels_(self):
        for i in range(0, self.rows):
            # Symbols
            symbol_labels = ctk.CTkLabel(self, text=self.labels["symbols"][i])
            symbol_labels.grid(row=i, column=0, padx=(10, 0), pady=(5, 0), sticky="W", )
            # Descriptions
            description_labels = ctk.CTkLabel(self, text=self.labels["descriptions"][i])
            description_labels.grid(row=i, column=1, padx=(10, 0), pady=(5, 0), sticky="W", )
            # Units
            unit_labels = ctk.CTkLabel(self, text=self.labels["units"][i])
            unit_labels.grid(row=i, column=3, padx=(10, 0), pady=(5, 0), sticky="W", )

    @staticmethod
    def numeric_input_validator(value: str) -> bool:
        pattern = "^\\d*[.]?\\d*([eE]?)[+-]?\\d*$"
        is_valid = re.search(pattern, value)
        return False if is_valid is None else True

    def convert_input(self) -> Tuple[bool, List[str | float]]:
        valid_input = []
        invalid_input = []
        for i in range(0, len(self.variables)):
            try:
                valid_input.append(float(self.variables[i].get()))
            except Exception as e:
                invalid_input.append(self.variables[i].__str__())
                print(e)

        if len(invalid_input) > 0:
            return False, invalid_input

        return True, valid_input

    def calculate(self):
        error, variables = self.convert_input()
        if error:
            try:
                Ned = variables[0]
                L = variables[1]
                E = variables[2] * 1_000_000
                A = variables[3] / 1_000_000
                I = variables[4] / 1_000_000_000_000
                i = variables[5] / 1000
                alpha_crit = variables[6]

                β = (sqrt((pi ** 2 * E * I) / (alpha_crit * Ned))) * (1 / L)
                λ = (β * L) / i
                self.output_label.configure(text=f"Súčiniteľ vzpernej dĺžky β={β:.2f}, Štíhlosť λ={λ:.2f}")
            except Exception as zde:
                tkinter.messagebox.showwarning("Upozornenie", "Delenie nulou!")

        else:
            tkinter.messagebox.showwarning("Upozornenie", f"{", ".join(variables)}: Nesprávne zadaný formát!")


if __name__ == "__main__":
    application = Alpha2BetaApp()
    application.mainloop()
