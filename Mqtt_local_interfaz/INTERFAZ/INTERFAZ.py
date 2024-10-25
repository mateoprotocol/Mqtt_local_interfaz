import tkinter as tk
from tkinter import ttk
import random
import csv
import paho.mqtt.client as mqtt
import re

# Configuración inicial
broker = "192.168.20.23"  # Cambia a 127.0.0.1 si es necesario
port = 1883  # Puerto por defecto de Mosquitto
topic = "categoria/rally"

filas = 12
table_data = [{"name": "", "value": ""} for i in range(filas)]

def update_table(new_message):
    global table_data
    try:
        # Convertir el nuevo mensaje a float para comparación numérica
        new_value = float(new_message)
        inserted = False

        # Buscar el lugar correcto para insertar el nuevo valor
        for i in range(len(table_data)):
            current_value = table_data[i]["value"]
            if current_value == "" or float(current_value) > new_value:
                # Insertar el nuevo valor y mantener el nombre de la fila
                if current_value == "":
                    # Si la celda está vacía, solo asignar el nuevo valor
                    table_data[i]["value"] = str(new_value)
                else:
                    # Insertar el nuevo valor antes del actual
                    table_data.insert(i, {"name": "", "value": str(new_value)})
                    inserted = True
                
                # Eliminar el último elemento si se excede el límite de 5
                if len(table_data) > filas:
                    table_data.pop()
                break
        
        # Si no se insertó y hay espacio, añadir el nuevo valor al final
        if not inserted and len(table_data) < filas:
            table_data.append({"name": f"Editable {len(table_data) + 1}", "value": str(new_value)})

        # Asegurar que solo tengamos filas registros
        table_data = table_data[:filas]

        # Actualiza la tabla visual
        refresh_table_view()

    except ValueError:
        print("Error: El mensaje debe ser un número válido")

def refresh_table_view():
    for i, data in enumerate(table_data):
        table.item(f'{i+1}', values=(i+1, data["name"], data["value"]))

# Función que maneja la recepción de mensajes

def on_message(client, userdata, msg):
    new_message = msg.payload.decode('utf-8')
    numero = re.search(r'\d+\.\d+|\d+', new_message)
    if "-" in new_message:
        pass
    elif numero:
        update_table(numero.group())
    else:    
        update_table(new_message)


# Configuración del cliente MQTT
client = mqtt.Client()
#  No se necesita usuario ni contraseña para Mosquitto local
client.connect(broker, port, 60)

client.subscribe(topic)
client.on_message = on_message

# # Comienza el loop MQTT en segundo plano
client.loop_start()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.geometry("700x500")  # AnchoxAlto: 
root.title("Posiciones")

# Variables para la edición de celdas
editable_entry = None
current_row = None

def edit_cell(event):
    global editable_entry, current_row
    try:
        # Seleccionar el ítem que fue clicado
        selected_item = table.selection()[0]
        current_row = selected_item
        
        # Obtener las coordenadas del clic
        column = table.identify_column(event.x)
        if column == '#2':  # La columna Editable ahora es la #2
            x, y, width, height = table.bbox(selected_item, 'Editable')
            
            # Crear el widget de entrada en la celda seleccionada
            editable_value = table.set(selected_item, 'Editable')
            editable_entry = tk.Entry(root)
            editable_entry.insert(0, editable_value)
            editable_entry.place(x=x, y=y, width=width, height=height)
            editable_entry.focus()
            
            # Guardar el valor cuando se presione Enter
            editable_entry.bind("<Return>", save_edit)
            # También guardar cuando el entry pierda el foco
            editable_entry.bind("<FocusOut>", save_edit)
    except IndexError:
        pass  # Si no hay selección, ignoramos el error

# Función para guardar los cambios de la celda editada
def save_edit(event):
    global editable_entry, current_row
    if editable_entry and current_row:
        new_value = editable_entry.get()
        # Guardar el nuevo valor en la tabla y en los datos
        table.set(current_row, 'Editable', new_value)
        row_index = int(current_row) - 1
        table_data[row_index]["name"] = new_value
        
        # Destruir el Entry después de guardar
        editable_entry.destroy()
        editable_entry = None

# Función para guardar los cambios en la primera columna editable
def save_changes():

    with open('datos.csv', mode='a', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["#","Nombre","Tiempo"])
        
        # Actualiza table_data con los valores actuales de la tabla
        for i in range(filas):
            table_data[i]["name"] = table.set(f'{i+1}', 'Editable')
            table_data[i]["value"] = table.set(f'{i+1}', 'Value')
            print(f"{i+1}-{table_data[i]['name']}-{table_data[i]['value']}")

            datos = [i+1,table_data[i]["name"],table_data[i]["value"]]
            escritor.writerow(datos)


   
    refresh_table_view()

# Creación de la tabla
columns = ('#', 'Editable', 'Value')  # Añadida la columna '#'
table = ttk.Treeview(root, columns=columns, show='headings')
table.heading('#', text='#')  # Encabezado para la numeración
table.heading('Editable', text='Nombre')
table.heading('Value', text='Tiempo(S)')

# Configurar el ancho de las columnas
table.column('#', width=50, anchor='center')  # Columna de numeración más estrecha
table.column('Editable', width=150)
table.column('Value', width=150)



# Añadir las filas iniciales a la tabla
for i in range(filas):
    table.insert('', 'end', iid=f'{i+1}', values=(i+1, table_data[i]["name"], table_data[i]["value"]))

table.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

# Vincular la tabla con el evento de doble clic para editar
table.bind("<Double-1>", edit_cell)

# Botón para guardar los cambios
save_button = tk.Button(root, text="Guardar", command=save_changes)
save_button.grid(row=1, column=0, pady=10)

def delete_row():
    try:
        row_number = int(delete_entry.get())  # Obtener el número de fila del cuadro de texto
        if 1 <= row_number <= filas:  # Verifica que el número esté en el rango válido
            # Eliminar el dato de table_data
            table_data[row_number - 1] = {"name": "", "value": ""}
            
            # Desplazar filas hacia arriba para llenar el espacio
            for i in range(row_number - 1, filas - 1):
                table_data[i] = table_data[i + 1]
            table_data[filas - 1] = {"name": "", "value": ""}  # Limpiar la última fila
            
            refresh_table_view()  # Actualiza la vista de la tabla
            delete_entry.delete(0, tk.END)  # Limpia el cuadro de texto
        else:
            print("Error: Número de fila no válido")
    except ValueError:
        print("Error: Ingrese un número válido")

def reset():
    
    for i in range(filas):
        table_data[i] = {"name": "", "value": ""}

    refresh_table_view()


def valor_random():
    a = round(random.uniform(1.1, 5.5), 2)
    update_table(a)

# Botón para agregar valores
add_button = tk.Button(root, text="add_value", command=valor_random)
add_button.grid(row=1, column=1, pady=10)

# Cuadro de texto y botón para borrar
delete_entry = tk.Entry(root, width=10)
delete_entry.grid(row=2, column=0, pady=10, padx=100, sticky='w')

delete_button = tk.Button(root, text="Borrar", command=delete_row)
delete_button.grid(row=2, column=0, columnspan=2, pady=10, padx=(5, 0), sticky='w')

reset_button = tk.Button(root, text="Resetear", command=reset)
reset_button.grid(row=2, column=1, columnspan=2, pady=10, padx=(5, 0), sticky='w')

# Ajustes de tamaño para la tabla
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# Inicia el loop principal de la interfaz
root.mainloop()

# Detiene el loop MQTT al cerrar la interfaz
client.loop_stop()
