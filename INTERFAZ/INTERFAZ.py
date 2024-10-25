import tkinter as tk
from tkinter import ttk
#import paho.mqtt.client as mqtt

# Configuración inicial
#broker = "192.168.188.179"  # Cambia a 127.0.0.1 si es necesario
#port = 1883  # Puerto por defecto de Mosquitto
#topic = "categoria/rally"
filas = 20
table_data = [{"name": f"Editable {i + 1}", "value": ""} for i in range(filas)]

def update_table(new_message):
    global table_data
    try:
        # Convertir el nuevo mensaje a float para comparación numérica
        new_value = float(new_message)
        
        # Encontrar la posición donde insertar el nuevo valor
        inserted = False
        for i in range(len(table_data)):
            current_value = table_data[i]["value"]
            if current_value == "" or float(current_value) > new_value:
                # Mover todos los elementos una posición hacia abajo
                table_data = table_data[:i] + [{"name": f"Posición {i+1}", "value": str(new_value)}] + table_data[i:-1]
                inserted = True
                break
        
        # Si no se insertó (es el peor tiempo), y hay espacio, añadirlo al final
        if not inserted and len(table_data) < 5:
            table_data = table_data[:-1] + [{"name": f"Posición {len(table_data)}", "value": str(new_value)}]
        
        # Asegurar que solo tengamos 5 registros
        table_data = table_data[:5]
        
        # Actualizar los nombres de las posiciones
        for i in range(len(table_data)):
            if table_data[i]["value"] != "":
                table_data[i]["name"] = f"Posición {i+1}"
        
        # Actualiza la tabla visual
        refresh_table_view()
    except ValueError:
        print("Error: El mensaje debe ser un número válido")

def refresh_table_view():
    # Actualiza la vista de la tabla con los datos actuales
    for i, data in enumerate(table_data):
        table.set(f'{i+1}', '#', str(i+1))
        table.set(f'{i+1}', 'Editable', data["name"])
        table.set(f'{i+1}', 'Value', data["value"])

# Función que maneja la recepción de mensajes
# def on_message(client, userdata, msg):
#     new_message = msg.payload.decode('utf-8')
#     if "-" in new_message:
#         pass
#     else:    
#         update_table(new_message)

# Configuración del cliente MQTT
# client = mqtt.Client()
# # No se necesita usuario ni contraseña para Mosquitto local
# client.connect(broker, port, 60)

# client.subscribe(topic)
# client.on_message = on_message

# # Comienza el loop MQTT en segundo plano
# client.loop_start()

# Configuración de la interfaz gráfica
root = tk.Tk()
root.geometry("400x500")# AnchoxAlto: 
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
    # Actualiza table_data con los valores actuales de la tabla
    for i in range(filas):
        table_data[i]["name"] = table.set(f'{i+1}', 'Editable')
        table_data[i]["value"] = table.set(f'{i+1}', 'Value')
        print(f"{i+1}-{table_data[i]['name']}-{table_data[i]['value']}")
    
    # Aquí podrías añadir código para guardar en un archivo o base de datos
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

table.grid(row=0, column=0, sticky='nsew')

# Vincular la tabla con el evento de doble clic para editar
table.bind("<Double-1>", edit_cell)

# Botón para guardar los cambios
save_button = tk.Button(root, text="Save Changes", command=save_changes)
save_button.grid(row=1, column=0, pady=10)

# Ajustes de tamaño para la tabla
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)



# Inicia el loop principal de la interfaz
root.mainloop()


# Detiene el loop MQTT al cerrar la interfaz
#client.loop_stop() 