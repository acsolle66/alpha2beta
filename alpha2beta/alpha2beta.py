import re
import tkinter.messagebox
from math import pi, sqrt
from typing import Tuple, List

import customtkinter as ctk


class Model:
    def __init__(self):
        self.__axial_force: float = 0
        self.__element_length: float = 0
        self.__elastic_modulus: float = 0
        self.__section_area: float = 0
        self.__second_area_moment: float = 0
        self.__gyration_radius: float = 0
        self.__critical_parameter: float = 0

    @staticmethod
    def __validate_input(value: str) -> bool:
        if value == "":
            return False
        if float(value) == 0:
            return False
        return True

    @property
    def axial_force(self) -> float:
        return self.__axial_force

    @axial_force.setter
    def axial_force(self, value: str) -> None:
        if self.__validate_input(value):
            self.__axial_force = float(value)
        else:
            raise ValueError("Neplatná hodnota Ned")

    @property
    def element_length(self) -> float:
        return self.__element_length

    @element_length.setter
    def element_length(self, value: str) -> None:
        if self.__validate_input(value):
            self.__element_length = float(value)
        else:
            raise ValueError("Neplatná hodnota L")

    @property
    def elastic_modulus(self) -> float:
        return self.__elastic_modulus

    @elastic_modulus.setter
    def elastic_modulus(self, value: str) -> None:
        if self.__validate_input(value):
            self.__elastic_modulus = float(value) * 1_000_000
        else:
            raise ValueError("Neplatná hodnota E")

    @property
    def section_area(self) -> float:
        return self.__section_area

    @section_area.setter
    def section_area(self, value: str) -> None:
        if self.__validate_input(value):
            self.__section_area = float(value) / 1_000_000
        else:
            raise ValueError("Neplatná hodnota A")

    @property
    def second_area_moment(self) -> float:
        return self.__second_area_moment

    @second_area_moment.setter
    def second_area_moment(self, value: str) -> None:
        if self.__validate_input(value):
            self.__second_area_moment = float(value) / 1_000_000_000_000
        else:
            raise ValueError("Neplatná hodnota I")

    @property
    def gyration_radius(self) -> float:
        return self.__gyration_radius

    @gyration_radius.setter
    def gyration_radius(self, value: str) -> None:

        if self.__validate_input(value):
            self.__gyration_radius = float(value) / 1000
        else:
            raise ValueError("Neplatná hodnota i")

    @property
    def critical_parameter(self) -> float:
        return self.__critical_parameter

    @critical_parameter.setter
    def critical_parameter(self, value: str) -> None:
        if self.__validate_input(value):
            self.__critical_parameter = float(value)
        else:
            raise Exception("Neplatná hodnota αcrit")

    def calculate_results(self) -> Tuple[float, float]:
        a: float = self.__critical_parameter * self.__axial_force
        if a == 0:
            raise Exception("Delenie nulou")

        b: float = (pi ** 2 * self.__elastic_modulus * self.__second_area_moment) / a
        if b < 0:
            raise Exception("Neplatná hodnota pod odmocninou")

        length_coefficient: float = sqrt(b) * (1 / self.__element_length)
        slimness: float = (length_coefficient * self.__element_length) / self.__gyration_radius

        return length_coefficient, slimness


class View(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.controller: Controller | None = None
        numeric_validator = self.register(self.numeric_input_validator)

        self.labels = {
            "descriptions": [" - Tlaková osová sila", " - Dĺžka prvku", " - Modul pružnosti", " - Plocha prvku",
                             " - Moment zotrvačnosti", " - Polomer zotrvačnosti",
                             " - Súčiniteľ kritickej sily"],
            "symbols": ["NEd", "L", "E", "A", "I", "i", "αcrit"],
            "units": ["[ kN ]", "[ m ]", "[ GPa ]", "[ mm² ]", "[ mm⁴ ]", "[ mm ]", "[ - ]"]}
        self.rows = len(self.labels["descriptions"])

        self._add_labels_()

        self.variables = [ctk.StringVar(value="0.000", name=self.labels["symbols"][i]) for i in range(0, self.rows)]

        self.entries = [
            ctk.CTkEntry(self, textvariable=variable, validate="all", validatecommand=(numeric_validator, "%P")) for
            variable in self.variables]
        for i in range(0, len(self.entries)):
            self.entries[i].grid(row=i, column=2, padx=(15, 0), pady=(5, 0), sticky="E")

        self.button_calc = ctk.CTkButton(self, text="Výpočet", command=self.calculate_button_press)
        self.button_calc.grid(row=8, column=0, columnspan=4, pady=(15, 0))

        self.output_label = ctk.CTkLabel(self, text="")
        self.output_label.grid(row=9, columnspan=4, padx=(5, 0), pady=(5, 0))

    @staticmethod
    def show_warning(message: str | Exception) -> None:
        tkinter.messagebox.showwarning("Upozornenie!", message)

    @staticmethod
    def numeric_input_validator(value: str) -> bool:
        pattern = "^([+-]?\\d*)[.]?\\d*((?<=\\d)[eE])?[+-]?\\d*$"
        is_valid = re.search(pattern, value)
        return False if is_valid is None else True

    def _add_labels_(self) -> None:
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

    def set_controller(self, controller) -> None:
        self.controller = controller

    def calculate_button_press(self) -> None:
        self.controller.calculate([variable.get() for variable in self.variables])

    def show_results(self, results: Tuple[float, float]) -> None:
        self.output_label.configure(text=f"Súčiniteľ vzpernej dĺžky β={results[0]:.2f}, Štíhlosť λ={results[1]:.2f}")


class Controller:
    def __init__(self, model: Model, view: View):
        self.model = model
        self.view = view

    def calculate(self, parameters: List[str]) -> None:
        try:
            self.__set_parameters(parameters)
            self.view.show_results(self.model.calculate_results())
        except Exception as error:
            self.view.show_warning(error)

    def __set_parameters(self, parameters: List[str]) -> None:
        try:
            self.model.axial_force = parameters[0]
            self.model.element_length = parameters[1]
            self.model.elastic_modulus = parameters[2]
            self.model.section_area = parameters[3]
            self.model.second_area_moment = parameters[4]
            self.model.gyration_radius = parameters[5]
            self.model.critical_parameter = parameters[6]
        except Exception as error:
            self.view.show_warning(error)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("alpha2beta")
        self.resizable(False, False)

        self.model: Model = Model()
        self.view: View = View(self)
        self.controller: Controller = Controller(self.model, self.view)

        self.view.set_controller(self.controller)
        self.view.grid(row=0, column=0, padx=10, pady=10)


if __name__ == "__main__":
    app = App()
    app.mainloop()
