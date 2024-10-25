import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt

# Configuración inicial
broker = "192.168.188.179"  # Cambia a 127.0.0.1 si es necesario
port = 1883  # Puerto por defecto de Mosquitto
topic = "categoria/rally"
messages = [""] * 5  # Lista para almacenar los últimos 5 mensajes

# Función que actualiza la tabla con los datos recibidos
def update_table(new_message):
    global messages
    messages = messages[1:] + [new_message]  # Mueve la lista y añade el nuevo mensaje
    for i, msg in enumerate(messages):
        table.set(f'{i+1}', 'Value', msg)  # Actualiza la columna "Value" con los mensajes

# Función que maneja la recepción de mensajes
def on_message(client, userdata, msg):
    new_message = msg.payload.decode('utf-8')
    if "-" in new_message:
        pass
    else:    
        update_table(new_message)

# Configuración del cliente MQTT
client = mqtt.Client()
# No se necesita usuario ni contraseña para Mosquitto local
client.connect(broker, port, 60)

client.subscribe(topic)
client.on_message = on_message

# Comienza el loop MQTT en segundo plano
client.loop_start()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("MQTT Data Table")

# Variables para la edición de celdas
editable_entry = None
current_row = None

# Función que inserta una entrada editable
def edit_cell(event):
    global editable_entry, current_row

    # Seleccionar el ítem que fue clicado
    selected_item = table.selection()[0]
    current_row = selected_item

    # Obtener las coordenadas del clic
    column = table.identify_column(event.x)
    if column == '#1':  # Asegurarse de que solo la primera columna sea editable
        x, y, width, height = table.bbox(selected_item, 'Editable')

        # Crear el widget de entrada (Entry) en la celda seleccionada
        editable_value = table.set(selected_item, 'Editable')
        editable_entry = tk.Entry(root)
        editable_entry.insert(0, editable_value)
        editable_entry.place(x=x, y=y, width=width, height=height)
        editable_entry.focus()

        # Guardar el valor cuando se presione Enter
        editable_entry.bind("<Return>", save_edit)

# Función para guardar los cambios de la celda editada
def save_edit(event):
    global editable_entry, current_row

    if editable_entry and current_row:
        new_value = editable_entry.get()

        # Guardar el nuevo valor en la tabla
        table.set(current_row, 'Editable', new_value)

        # Destruir el Entry después de guardar
        editable_entry.destroy()
        editable_entry = None

# Creación de la tabla
columns = ('Editable', 'Value')
table = ttk.Treeview(root, columns=columns, show='headings')

table.heading('Editable', text='Nombre')
table.heading('Value', text='Tiempo(S)')

# Añadir las filas a la tabla
for i in range(5):
    table.insert('', 'end', iid=f'{i+1}', values=(f'Editable {i+1}', messages[i]))

table.grid(row=0, column=0, sticky='nsew')

# Vincular la tabla con el evento de doble clic para editar
table.bind("<Double-1>", edit_cell)

# Función para guardar los cambios en la primera columna editable
def save_changes():
    for i in range(5):
        editable_value = table.set(f'{i+1}', 'Editable')
        print(f"Editable Field {i+1}: {editable_value}")

# Botón para guardar los cambios
save_button = tk.Button(root, text="Save Changes", command=save_changes)
save_button.grid(row=1, column=0, pady=10)

# Ajustes de tamaño para la tabla
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Inicia el loop principal de la interfaz
root.mainloop()

# Detiene el loop MQTT al cerrar la interfaz
client.loop_stop()
