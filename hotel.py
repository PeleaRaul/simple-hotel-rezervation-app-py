# hotel_reservation_app_with_xml_fixed.py
import tkinter as tk
from tkinter import messagebox
import xml.etree.ElementTree as ET
import os
from tkcalendar import DateEntry
from datetime import datetime, timedelta

class Room:
    def __init__(self, room_number, room_type, status="free"):
        self.room_number = room_number
        self.room_type = room_type
        self.status = status

    def __str__(self):
        return f"Room {self.room_number} - Type: {self.room_type} - Status: {self.status}"

class Reservation:
    reservations = []

    @classmethod
    def add_reservation(cls, reservation):
        cls.reservations.append(reservation)
        cls.save_to_xml()

    @classmethod
    def delete_reservation(cls, reservation):
        cls.reservations.remove(reservation)
        cls.save_to_xml()

    @classmethod
    def cancel_reservation(cls, reservation_index):
        if 0 <= reservation_index < len(cls.reservations):
            reservation = cls.reservations.pop(reservation_index)
            room_info = reservation.split(" - ")[1]
            room_number = int(room_info.split()[1])
            room = room_dict.get(str(room_number))

            if room:
                room.status = "free"
                cls.save_to_xml()
            else:
                show_message("Invalid room information.")
        else:
            show_message("Invalid reservation index.")

    @staticmethod
    def display_reservations():
        if not Reservation.reservations:
            return "No reservations available."
        else:
            return "\n".join(Reservation.reservations)

    @staticmethod
    def save_to_xml(filename=os.path.expanduser("~/reservations.xml")):
        root = ET.Element("reservations")

        if Reservation.reservations:
            for res in Reservation.reservations:
                elem = ET.SubElement(root, "reservation")
                elem.text = res
        else:
            elem = ET.SubElement(root, "message")
            elem.text = "No reservations available."

        tree = ET.ElementTree(root)
        tree.write(filename)

    @staticmethod
    def load_from_xml(filename=os.path.expanduser("~/reservations.xml")):
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
            Reservation.reservations = [elem.text for elem in root.findall(".//reservation")]
        except FileNotFoundError:
            pass

def reservation_decorator(func):
    def wrapper(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], Room) and args[1].status == "occupied":
            show_message("Cannot perform action. Room is already occupied.")
        else:
            func(*args, **kwargs)
    return wrapper

@reservation_decorator
def make_reservation(customer_name, room, arrival_date, departure_date):
    room.status = "occupied"
    reservation = f"Reservation for {customer_name} - {room} - Arrival: {arrival_date} - Departure: {departure_date}"
    Reservation.add_reservation(reservation)

@reservation_decorator
def cancel_reservation(reservation_index):
    if not Reservation.reservations:
        show_message("No reservations to cancel.")
        return

    if 0 <= reservation_index < len(Reservation.reservations):
        reservation = Reservation.reservations.pop(reservation_index)
        room_info = reservation.split(" - ")[1]
        room_number = int(room_info.split()[1])
        room = room_dict.get(str(room_number))

        if room:
            room.status = "free"
            Reservation.save_to_xml()
            show_message("Reservation canceled.")
            refresh_room_status()
        else:
            show_message("Invalid room information.")
    else:
        show_message("Invalid reservation index.")

def show_message(message):
    messagebox.showinfo("Hotel Reservation App", message)

def make_reservation_gui():
    customer_name = entry_name.get()
    selected_room = room_var.get()
    arrival_date = cal_arrival.get_date()
    departure_date = cal_departure.get_date()

    if selected_room:
        room = room_dict[selected_room]
        make_reservation(customer_name, room, arrival_date, departure_date)
        show_message(f"Reservation successful for {customer_name} - Room {room.room_number}")
        refresh_room_status()

def cancel_reservation_gui():
    selected_reservation = listbox_reservations.curselection()

    if not selected_reservation:
        show_message("Please select a reservation to cancel.")
        return

    index_to_cancel = int(selected_reservation[0])

    if 0 <= index_to_cancel < len(Reservation.reservations):
        cancel_reservation(index_to_cancel)
        show_message("Reservation canceled.")
        refresh_room_status()
    else:
        show_message("Invalid reservation index.")

def refresh_room_status():
    listbox_reservations.delete(0, tk.END)
    listbox_room_status.delete(0, tk.END)

    # Update the room status based on reservations
    for reservation in Reservation.reservations:
        room_info = reservation.split(" - ")[1]
        room_number = int(room_info.split()[1])
        room = room_dict.get(str(room_number))

        if room:
            room.status = "occupied"

    # Clear and update the room status listbox
    for room_number, room in room_dict.items():
        status_text = f"Room {room_number}: {room.status.capitalize()}"
        listbox_room_status.insert(tk.END, status_text)

    # Clear and update the reservations listbox
    for i, reservation in enumerate(Reservation.reservations, start=1):
        listbox_reservations.insert(tk.END, f"{i}. {reservation}")

def open_file_location():
    xml_location = os.path.expanduser("~/reservations.xml")
    os.system("explorer /select," + xml_location)


def add_room_popup():
    # Create a new popup window
    room_popup = tk.Toplevel(root)
    room_popup.title("Add Room")

    # Labels and Entry widgets for Room Number and Room Type
    label_room_number = tk.Label(room_popup, text="Room Number:")
    label_room_number.grid(row=0, column=0, padx=5, pady=5)

    entry_room_number = tk.Entry(room_popup)
    entry_room_number.grid(row=0, column=1, padx=5, pady=5)

    label_room_type = tk.Label(room_popup, text="Room Type:")
    label_room_type.grid(row=1, column=0, padx=5, pady=5)

    room_types = ["single", "double", "suite"]
    room_type_var = tk.StringVar(room_popup)
    room_type_var.set(room_types[0])  # Set the default value

    dropdown_room_type = tk.OptionMenu(room_popup, room_type_var, *room_types)
    dropdown_room_type.grid(row=1, column=1, padx=5, pady=5)

    # Button to add the room
    btn_add_room = tk.Button(room_popup, text="Add Room", command=lambda: save_and_close(room_popup, entry_room_number.get(), room_type_var.get()))
    btn_add_room.grid(row=2, column=0, columnspan=2, pady=10)

def save_and_close(room_popup, room_number, room_type):
    # Validate the input
    if not room_number.isdigit():
        show_message("Please enter a valid room number.")
        return

    # Check if the room number already exists
    if room_number in room_dict:
        show_message(f"Room {room_number} already exists.")
        return

    # Create a new Room instance and add it to the room_dict
    new_room = Room(int(room_number), room_type)
    room_dict[str(new_room.room_number)] = new_room

    # Save the updated room_dict to rooms.xml
    save_rooms_to_xml()

    # Close the popup
    room_popup.destroy()

def save_rooms_to_xml(filename=os.path.expanduser("~/rooms.xml")):
    root = ET.Element("rooms")

    for room_number, room in room_dict.items():
        elem = ET.SubElement(root, "room", number=str(room.room_number), type=room.room_type)

    tree = ET.ElementTree(root)
    tree.write(filename)

# Sample Rooms
room1 = Room(1, "single")
room2 = Room(2, "double")
room3 = Room(3, "suite")

# Initialize room_dict with the sample rooms
room_dict = {str(room.room_number): room for room in [room1, room2, room3]}

Reservation.load_from_xml()

root = tk.Tk()
root.title("Hotel Reservation App")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_name = tk.Label(frame, text="Customer Name:")
label_name.grid(row=0, column=0, padx=5, pady=5)

entry_name = tk.Entry(frame)
entry_name.grid(row=0, column=1, padx=5, pady=5)

label_arrival = tk.Label(frame, text="Arrival Date:")
label_arrival.grid(row=1, column=0, padx=5, pady=5)

cal_arrival = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
cal_arrival.grid(row=1, column=1, padx=5, pady=5)

label_departure = tk.Label(frame, text="Departure Date:")
label_departure.grid(row=2, column=0, padx=5, pady=5)

cal_departure = DateEntry(frame, width=12, background='darkblue', foreground='white', borderwidth=2)
cal_departure.grid(row=2, column=1, padx=5, pady=5)

label_rooms = tk.Label(frame, text="Available Rooms:")
label_rooms.grid(row=3, column=0, padx=5, pady=5)

room_var = tk.StringVar()
room_var.set("")

# Update the dropdown menu whenever it is opened
def update_dropdown_menu(*args):
    menu = dropdown_rooms["menu"]
    menu.delete(0, "end")
    for room_number in room_dict.keys():
        menu.add_command(label=room_number, command=lambda value=room_number: room_var.set(value))

dropdown_rooms = tk.OptionMenu(frame, room_var, *room_dict.keys())
dropdown_rooms.grid(row=3, column=1, padx=5, pady=5)

# Bind the update_dropdown_menu function to the dropdown menu
room_var.trace("w", update_dropdown_menu)

btn_reserve = tk.Button(frame, text="Make Reservation", command=make_reservation_gui)
btn_reserve.grid(row=4, column=0, columnspan=2, pady=10)

listbox_reservations = tk.Listbox(frame, selectmode=tk.SINGLE, width=100)
listbox_reservations.grid(row=5, column=0, pady=10)

listbox_room_status = tk.Listbox(frame, selectmode=tk.SINGLE, width=100)
listbox_room_status.grid(row=5, column=1, pady=10)

refresh_room_status()

btn_cancel = tk.Button(frame, text="Cancel Reservation", command=cancel_reservation_gui)
btn_cancel.grid(row=6, column=0, columnspan=2, pady=10)

btn_refresh = tk.Button(frame, text="Refresh", command=refresh_room_status)
btn_refresh.grid(row=7, column=0, columnspan=2, pady=10)

btn_add_room = tk.Button(frame, text="Add Room", command=add_room_popup)
btn_add_room.grid(row=8, column=0, columnspan=2, pady=10)

btn_open_location = tk.Button(frame, text="Go to File Location", command=open_file_location)
btn_open_location.grid(row=9, column=0, columnspan=2, pady=10)

root.mainloop()
