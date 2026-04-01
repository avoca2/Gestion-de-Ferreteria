#!/usr/bin/env python3
"""
Sistema de Gestión Ferretería Don Willy - Interfaz Gráfica Simplificada
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sys
import os

# Intentar importar Config
try:
    from config import Config
except ImportError as e:
    print(f"Error importando config: {e}")
    print("Creando config básica...")
    
    class Config:
        SQLITE_DB_PATH = "don_willy.db"
        EMPRESA_NOMBRE = "FERRETERÍA DON WILLY"
        IVA_PORCENTAJE = 0.19
        PRIMARY_COLOR = "#2c3e50"
        SECONDARY_COLOR = "#3498db"
        SUCCESS_COLOR = "#27ae60"
        DANGER_COLOR = "#e74c3c"
        WARNING_COLOR = "#f39c12"
        LIGHT_BG = "#ecf0f1"
        DARK_TEXT = "#2c3e50"

class SistemaFerreteriaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{Config.EMPRESA_NOMBRE} - Sistema de Gestión")
        self.root.geometry("1100x650")
        self.root.configure(bg=Config.LIGHT_BG)
        
        # Inicializar base de datos
        self.init_database()
        
        # Variables para el carrito
        self.carrito = []
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar datos iniciales
        self.cargar_productos()
        self.cargar_clientes()
        self.actualizar_reportes()
        
    def init_database(self):
        """Inicializar base de datos"""
        self.conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Crear tablas si no existen"""
        try:
            # Tabla productos
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo VARCHAR(50) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    descripcion TEXT,
                    categoria VARCHAR(50),
                    precio_compra DECIMAL(10,2) NOT NULL,
                    precio_venta DECIMAL(10,2) NOT NULL,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    proveedor VARCHAR(100),
                    fecha_ingreso DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Tabla clientes
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rut VARCHAR(20) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    telefono VARCHAR(20),
                    email VARCHAR(100),
                    direccion TEXT,
                    tipo_cliente VARCHAR(20) DEFAULT 'normal',
                    fecha_registro DATE DEFAULT CURRENT_DATE
                )
            ''')
            
            # Tabla ventas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_folio VARCHAR(50) UNIQUE NOT NULL,
                    cliente_id INTEGER,
                    fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                    subtotal DECIMAL(10,2) NOT NULL,
                    iva DECIMAL(10,2) NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    metodo_pago VARCHAR(20),
                    estado VARCHAR(20) DEFAULT 'completada',
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                )
            ''')
            
            # Tabla detalle_ventas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario DECIMAL(10,2) NOT NULL,
                    total_linea DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas(id),
                    FOREIGN KEY (producto_id) REFERENCES productos(id)
                )
            ''')
            
            self.conn.commit()
            print("✅ Tablas creadas/verificadas correctamente")
            
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
            messagebox.showerror("Error", f"No se pudo inicializar la base de datos: {e}")
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text=Config.EMPRESA_NOMBRE,
                              font=('Arial', 20, 'bold'),
                              bg=Config.PRIMARY_COLOR,
                              fg='white')
        title_label.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Notebook (pestañas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear las pestañas
        self.create_tab_productos()
        self.create_tab_clientes()
        self.create_tab_ventas()
        self.create_tab_reportes()
        
        # Barra de estado
        self.status_bar = tk.Label(self.root, 
                                   text="Sistema Don Willy Ferretería - Listo",
                                   bg=Config.PRIMARY_COLOR,
                                   fg='white',
                                   anchor=tk.W,
                                   relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_tab_productos(self):
        """Crear pestaña de productos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📦 Productos")
        
        # Frame superior (botones)
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(top_frame, text="➕ Nuevo", 
                 command=self.nuevo_producto,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="✏️ Editar", 
                 command=self.editar_producto,
                 bg=Config.WARNING_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🗑️ Eliminar", 
                 command=self.eliminar_producto,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🔄 Actualizar", 
                 command=self.cargar_productos,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Frame de búsqueda
        search_frame = ttk.Frame(tab)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:", 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.producto_search = tk.Entry(search_frame, width=40, font=('Arial', 10))
        self.producto_search.pack(side=tk.LEFT, padx=5)
        self.producto_search.bind('<KeyRelease>', self.buscar_productos)
        
        # Treeview para productos
        frame_tree = ttk.Frame(tab)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Código', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Mínimo')
        self.tree_productos = ttk.Treeview(frame_tree, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_productos.heading(col, text=col)
            width = 80
            if col == 'Nombre': width = 200
            if col == 'ID': width = 50
            self.tree_productos.column(col, width=width, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_productos.yview)
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree_productos.xview)
        self.tree_productos.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree_productos.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Info
        self.label_info_productos = tk.Label(tab, text="Total productos: 0", 
                                            font=('Arial', 10, 'bold'),
                                            bg=Config.LIGHT_BG)
        self.label_info_productos.pack(pady=10)
    
    def create_tab_clientes(self):
        """Crear pestaña de clientes"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Clientes")
        
        # Frame superior
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(top_frame, text="➕ Nuevo", 
                 command=self.nuevo_cliente,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="✏️ Editar", 
                 command=self.editar_cliente,
                 bg=Config.WARNING_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🗑️ Eliminar", 
                 command=self.eliminar_cliente,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🔄 Actualizar", 
                 command=self.cargar_clientes,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Treeview para clientes
        frame_tree = ttk.Frame(tab)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'RUT', 'Nombre', 'Teléfono', 'Email', 'Tipo')
        self.tree_clientes = ttk.Treeview(frame_tree, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_clientes.heading(col, text=col)
            width = 100
            if col == 'Nombre': width = 150
            if col == 'Email': width = 150
            if col == 'ID': width = 50
            self.tree_clientes.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_clientes.yview)
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree_clientes.xview)
        self.tree_clientes.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_clientes.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Info
        self.label_info_clientes = tk.Label(tab, text="Total clientes: 0", 
                                           font=('Arial', 10, 'bold'),
                                           bg=Config.LIGHT_BG)
        self.label_info_clientes.pack(pady=10)
    
    def create_tab_ventas(self):
        """Crear pestaña de ventas"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💰 Ventas")
        
        # Dividir en dos frames
        left_frame = ttk.Frame(tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # === LADO IZQUIERDO: Productos ===
        tk.Label(left_frame, text="🛒 Productos Disponibles", 
                font=('Arial', 12, 'bold'),
                bg=Config.LIGHT_BG).pack(pady=(0, 10))
        
        # Búsqueda
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_venta = tk.Entry(search_frame, width=30)
        self.search_venta.pack(side=tk.LEFT, padx=5)
        self.search_venta.bind('<KeyRelease>', self.buscar_productos_venta)
        
        # Lista de productos
        frame_tree = ttk.Frame(left_frame)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Producto', 'Precio', 'Stock')
        self.tree_productos_venta = ttk.Treeview(frame_tree, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree_productos_venta.heading(col, text=col)
            width = 80
            if col == 'Producto': width = 150
            self.tree_productos_venta.column(col, width=width)
        
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_productos_venta.yview)
        self.tree_productos_venta.configure(yscrollcommand=vsb.set)
        
        self.tree_productos_venta.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Botón para agregar al carrito
        tk.Button(left_frame, text="➕ Agregar al Carrito", 
                 command=self.agregar_al_carrito,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(pady=10)
        
        # === LADO DERECHO: Carrito ===
        tk.Label(right_frame, text="🛍️ Carrito de Compra", 
                font=('Arial', 12, 'bold'),
                bg=Config.LIGHT_BG).pack(pady=(0, 10))
        
        # Treeview del carrito
        frame_tree_carrito = ttk.Frame(right_frame)
        frame_tree_carrito.pack(fill=tk.BOTH, expand=True)
        
        columns_carrito = ('Producto', 'Cantidad', 'Precio', 'Total')
        self.tree_carrito = ttk.Treeview(frame_tree_carrito, columns=columns_carrito, show='headings', height=10)
        
        for col in columns_carrito:
            self.tree_carrito.heading(col, text=col)
            self.tree_carrito.column(col, width=90)
        
        vsb_carrito = ttk.Scrollbar(frame_tree_carrito, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=vsb_carrito.set)
        
        self.tree_carrito.grid(row=0, column=0, sticky='nsew')
        vsb_carrito.grid(row=0, column=1, sticky='ns')
        
        frame_tree_carrito.grid_rowconfigure(0, weight=1)
        frame_tree_carrito.grid_columnconfigure(0, weight=1)
        
        # Botones del carrito
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="➖ Quitar", 
                 command=self.quitar_del_carrito,
                 bg=Config.WARNING_COLOR,
                 fg='white',
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🗑️ Vaciar", 
                 command=self.vaciar_carrito,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Totales
        total_frame = tk.Frame(right_frame, bg=Config.LIGHT_BG)
        total_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(total_frame, text="Subtotal:", 
                font=('Arial', 10, 'bold'),
                bg=Config.LIGHT_BG).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_subtotal = tk.Label(total_frame, text="$0", font=('Arial', 10), bg=Config.LIGHT_BG)
        self.label_subtotal.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(total_frame, text=f"IVA ({Config.IVA_PORCENTAJE*100}%):", 
                font=('Arial', 10, 'bold'),
                bg=Config.LIGHT_BG).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_iva = tk.Label(total_frame, text="$0", font=('Arial', 10), bg=Config.LIGHT_BG)
        self.label_iva.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(total_frame, text="TOTAL:", 
                font=('Arial', 11, 'bold'),
                bg=Config.LIGHT_BG).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_total = tk.Label(total_frame, text="$0", 
                                   font=('Arial', 11, 'bold'),
                                   fg=Config.SUCCESS_COLOR,
                                   bg=Config.LIGHT_BG)
        self.label_total.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Botón finalizar venta
        tk.Button(right_frame, text="✅ FINALIZAR VENTA", 
                 command=self.finalizar_venta,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2).pack(fill=tk.X, pady=10)
    
    def create_tab_reportes(self):
        """Crear pestaña de reportes"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Reportes")
        
        # Frame para estadísticas
        stats_frame = tk.LabelFrame(tab, text="📈 Estadísticas Generales", 
                                   font=('Arial', 11, 'bold'),
                                   bg=Config.LIGHT_BG,
                                   padx=10, pady=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear grid para estadísticas
        grid_frame = tk.Frame(stats_frame, bg=Config.LIGHT_BG)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estadísticas
        self.label_total_productos = tk.Label(grid_frame, 
                                             text="Total Productos: Cargando...",
                                             font=('Arial', 10, 'bold'),
                                             bg=Config.LIGHT_BG)
        self.label_total_productos.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_productos_bajo = tk.Label(grid_frame,
                                            text="Productos con Stock Bajo: Cargando...",
                                            font=('Arial', 10, 'bold'),
                                            bg=Config.LIGHT_BG)
        self.label_productos_bajo.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_total_clientes = tk.Label(grid_frame,
                                            text="Total Clientes: Cargando...",
                                            font=('Arial', 10, 'bold'),
                                            bg=Config.LIGHT_BG)
        self.label_total_clientes.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_ventas_hoy = tk.Label(grid_frame,
                                        text="Ventas Hoy: Cargando...",
                                        font=('Arial', 10, 'bold'),
                                        bg=Config.LIGHT_BG)
        self.label_ventas_hoy.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Botón para actualizar
        tk.Button(stats_frame, text="🔄 Actualizar Reportes",
                 command=self.actualizar_reportes,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(pady=10)
    
    # ========== MÉTODOS PARA PRODUCTOS ==========
    
    def cargar_productos(self, search_term=""):
        """Cargar productos en el Treeview"""
        # Limpiar treeview
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        try:
            # Consultar productos
            if search_term:
                query = "SELECT * FROM productos WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY nombre"
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                query = "SELECT * FROM productos ORDER BY nombre"
                params = ()
            
            self.cursor.execute(query, params)
            productos = self.cursor.fetchall()
            
            # Insertar en treeview
            for producto in productos:
                self.tree_productos.insert('', tk.END, values=(
                    producto['id'],
                    producto['codigo'],
                    producto['nombre'],
                    producto['categoria'],
                    f"${producto['precio_venta']:,.0f}",
                    producto['stock'],
                    producto['stock_minimo']
                ))
            
            # Actualizar información
            self.label_info_productos.config(text=f"Total productos: {len(productos)}")
            
            # También cargar en pestaña de ventas
            self.buscar_productos_venta()
            
        except Exception as e:
            print(f"Error al cargar productos: {e}")
    
    def buscar_productos(self, event=None):
        """Buscar productos según término"""
        search_term = self.producto_search.get()
        self.cargar_productos(search_term)
    
    def nuevo_producto(self):
        """Abrir formulario para nuevo producto"""
        self.dialogo_producto(None)
    
    def editar_producto(self):
        """Editar producto seleccionado"""
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        item = self.tree_productos.item(selection[0])
        producto_id = item['values'][0]
        
        # Obtener datos del producto
        self.cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        producto = self.cursor.fetchone()
        
        if producto:
            self.dialogo_producto(producto)
    
    def eliminar_producto(self):
        """Eliminar producto seleccionado"""
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        item = self.tree_productos.item(selection[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][2]
        
        respuesta = messagebox.askyesno("Confirmar", 
                                        f"¿Eliminar el producto: {producto_nombre}?")
        
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                self.conn.commit()
                self.cargar_productos()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def dialogo_producto(self, producto):
        """Diálogo para agregar/editar producto"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Producto" if producto is None else "Editar Producto")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=Config.LIGHT_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos del formulario
        campos = [
            ("Código:", "codigo", 0),
            ("Nombre:", "nombre", 1),
            ("Descripción:", "descripcion", 2),
            ("Categoría:", "categoria", 3),
            ("Precio Compra:", "precio_compra", 4),
            ("Precio Venta:", "precio_venta", 5),
            ("Stock:", "stock", 6),
            ("Stock Mínimo:", "stock_minimo", 7),
            ("Proveedor:", "proveedor", 8)
        ]
        
        entries = {}
        
        for label_text, field_name, row in campos:
            tk.Label(main_frame, text=label_text, bg=Config.LIGHT_BG).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if field_name == 'descripcion':
                entry = tk.Text(main_frame, height=4, width=40)
                entry.grid(row=row, column=1, pady=5)
            else:
                entry = tk.Entry(main_frame, width=40)
                entry.grid(row=row, column=1, pady=5)
            
            entries[field_name] = entry
            
            # Si hay datos, llenar campos
            if producto:
                if field_name == 'descripcion':
                    entry.insert('1.0', producto[field_name])
                else:
                    entry.insert(0, str(producto[field_name]))
        
        def guardar():
            try:
                producto_data = {}
                for field_name, entry in entries.items():
                    if field_name == 'descripcion':
                        producto_data[field_name] = entry.get('1.0', tk.END).strip()
                    else:
                        producto_data[field_name] = entry.get().strip()
                
                # Validar
                if not producto_data['codigo'] or not producto_data['nombre']:
                    messagebox.showwarning("Advertencia", "Código y Nombre son obligatorios")
                    return
                
                # Convertir números
                producto_data['precio_compra'] = float(producto_data['precio_compra'] or 0)
                producto_data['precio_venta'] = float(producto_data['precio_venta'] or 0)
                producto_data['stock'] = int(producto_data['stock'] or 0)
                producto_data['stock_minimo'] = int(producto_data['stock_minimo'] or 5)
                
                if producto:
                    # Actualizar
                    self.cursor.execute('''
                        UPDATE productos SET
                            codigo=?, nombre=?, descripcion=?, categoria=?,
                            precio_compra=?, precio_venta=?, stock=?,
                            stock_minimo=?, proveedor=?
                        WHERE id=?
                    ''', (
                        producto_data['codigo'],
                        producto_data['nombre'],
                        producto_data['descripcion'],
                        producto_data['categoria'],
                        producto_data['precio_compra'],
                        producto_data['precio_venta'],
                        producto_data['stock'],
                        producto_data['stock_minimo'],
                        producto_data['proveedor'],
                        producto['id']
                    ))
                    mensaje = "✅ Producto actualizado"
                else:
                    # Insertar nuevo
                    self.cursor.execute('''
                        INSERT INTO productos 
                        (codigo, nombre, descripcion, categoria, precio_compra,
                         precio_venta, stock, stock_minimo, proveedor)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        producto_data['codigo'],
                        producto_data['nombre'],
                        producto_data['descripcion'],
                        producto_data['categoria'],
                        producto_data['precio_compra'],
                        producto_data['precio_venta'],
                        producto_data['stock'],
                        producto_data['stock_minimo'],
                        producto_data['proveedor']
                    ))
                    mensaje = "✅ Producto agregado"
                
                self.conn.commit()
                self.cargar_productos()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese números válidos en precio y stock")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=Config.LIGHT_BG)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar", 
                 command=guardar,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancelar", 
                 command=dialog.destroy,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
    
    # ========== MÉTODOS PARA CLIENTES ==========
    
    def cargar_clientes(self):
        """Cargar clientes en el Treeview"""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM clientes ORDER BY nombre")
            clientes = self.cursor.fetchall()
            
            for cliente in clientes:
                self.tree_clientes.insert('', tk.END, values=(
                    cliente['id'],
                    cliente['rut'],
                    cliente['nombre'],
                    cliente['telefono'],
                    cliente['email'],
                    cliente['tipo_cliente']
                ))
            
            self.label_info_clientes.config(text=f"Total clientes: {len(clientes)}")
            
        except Exception as e:
            print(f"Error al cargar clientes: {e}")
    
    def nuevo_cliente(self):
        """Abrir formulario para nuevo cliente"""
        self.dialogo_cliente(None)
    
    def editar_cliente(self):
        """Editar cliente seleccionado"""
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = self.cursor.fetchone()
        
        if cliente:
            self.dialogo_cliente(cliente)
    
    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        cliente_nombre = item['values'][2]
        
        respuesta = messagebox.askyesno("Confirmar", 
                                        f"¿Eliminar al cliente: {cliente_nombre}?")
        
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                self.conn.commit()
                self.cargar_clientes()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", "Cliente eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def dialogo_cliente(self, cliente):
        """Diálogo para agregar/editar cliente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Cliente" if cliente is None else "Editar Cliente")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=Config.LIGHT_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ("RUT:", "rut", 0),
            ("Nombre:", "nombre", 1),
            ("Teléfono:", "telefono", 2),
            ("Email:", "email", 3),
            ("Dirección:", "direccion", 4)
        ]
        
        entries = {}
        
        for label_text, field_name, row in campos:
            tk.Label(main_frame, text=label_text, bg=Config.LIGHT_BG).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if field_name == 'direccion':
                entry = tk.Text(main_frame, height=3, width=30)
                entry.grid(row=row, column=1, pady=5)
            else:
                entry = tk.Entry(main_frame, width=30)
                entry.grid(row=row, column=1, pady=5)
            
            entries[field_name] = entry
            
            if cliente:
                if field_name == 'direccion':
                    entry.insert('1.0', cliente[field_name])
                else:
                    entry.insert(0, str(cliente[field_name]))
        
        # Tipo de cliente
        tk.Label(main_frame, text="Tipo:", bg=Config.LIGHT_BG).grid(row=5, column=0, sticky=tk.W, pady=5)
        tipo_var = tk.StringVar(value=cliente['tipo_cliente'] if cliente else 'normal')
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var, 
                                 values=['normal', 'preferencial', 'mayorista'], 
                                 width=28, state='readonly')
        tipo_combo.grid(row=5, column=1, pady=5)
        
        def guardar():
            try:
                cliente_data = {}
                for field_name, entry in entries.items():
                    if field_name == 'direccion':
                        cliente_data[field_name] = entry.get('1.0', tk.END).strip()
                    else:
                        cliente_data[field_name] = entry.get().strip()
                
                cliente_data['tipo_cliente'] = tipo_var.get()
                
                if not cliente_data['rut'] or not cliente_data['nombre']:
                    messagebox.showwarning("Advertencia", "RUT y Nombre son obligatorios")
                    return
                
                if cliente:
                    # Actualizar
                    self.cursor.execute('''
                        UPDATE clientes SET
                            rut=?, nombre=?, telefono=?, email=?,
                            direccion=?, tipo_cliente=?
                        WHERE id=?
                    ''', (
                        cliente_data['rut'],
                        cliente_data['nombre'],
                        cliente_data['telefono'],
                        cliente_data['email'],
                        cliente_data['direccion'],
                        cliente_data['tipo_cliente'],
                        cliente['id']
                    ))
                    mensaje = "✅ Cliente actualizado"
                else:
                    # Insertar nuevo
                    self.cursor.execute('''
                        INSERT INTO clientes 
                        (rut, nombre, telefono, email, direccion, tipo_cliente)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        cliente_data['rut'],
                        cliente_data['nombre'],
                        cliente_data['telefono'],
                        cliente_data['email'],
                        cliente_data['direccion'],
                        cliente_data['tipo_cliente']
                    ))
                    mensaje = "✅ Cliente agregado"
                
                self.conn.commit()
                self.cargar_clientes()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=Config.LIGHT_BG)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar", 
                 command=guardar,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="❌ Cancelar", 
                 command=dialog.destroy,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
    
    # ========== MÉTODOS PARA VENTAS ==========
    
    def buscar_productos_venta(self, event=None):
        """Buscar productos para venta"""
        search_term = self.search_venta.get()
        
        # Limpiar treeview
        for item in self.tree_productos_venta.get_children():
            self.tree_productos_venta.delete(item)
        
        try:
            if search_term:
                query = "SELECT * FROM productos WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY nombre"
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                query = "SELECT * FROM productos WHERE stock > 0 ORDER BY nombre LIMIT 50"
                params = ()
            
            self.cursor.execute(query, params)
            productos = self.cursor.fetchall()
            
            for producto in productos:
                self.tree_productos_venta.insert('', tk.END, values=(
                    producto['id'],
                    producto['nombre'],
                    f"${producto['precio_venta']:,.0f}",
                    producto['stock']
                ))
                
        except Exception as e:
            print(f"Error al buscar productos venta: {e}")
    
    def agregar_al_carrito(self):
        """Agregar producto seleccionado al carrito"""
        selection = self.tree_productos_venta.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree_productos_venta.item(selection[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][1]
        precio = float(item['values'][2].replace('$', '').replace(',', ''))
        stock = item['values'][3]
        
        # Diálogo para cantidad
        dialog = tk.Toplevel(self.root)
        dialog.title("Cantidad")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Producto: {producto_nombre}").pack(pady=10)
        tk.Label(dialog, text=f"Stock: {stock}").pack()
        
        cantidad_var = tk.StringVar(value="1")
        tk.Entry(dialog, textvariable=cantidad_var, width=10).pack(pady=10)
        
        def agregar():
            try:
                cantidad = int(cantidad_var.get())
                if cantidad <= 0:
                    messagebox.showwarning("Error", "Cantidad debe ser > 0")
                    return
                
                if cantidad > stock:
                    messagebox.showwarning("Error", f"Stock insuficiente. Disponible: {stock}")
                    return
                
                # Agregar al carrito (treeview)
                total = cantidad * precio
                self.tree_carrito.insert('', tk.END, values=(
                    producto_nombre,
                    cantidad,
                    f"${precio:,.0f}",
                    f"${total:,.0f}"
                ))
                
                # Actualizar totales
                self.calcular_totales()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese número válido")
        
        tk.Button(dialog, text="Agregar", command=agregar).pack()
    
    def quitar_del_carrito(self):
        """Quitar producto del carrito"""
        selection = self.tree_carrito.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
            return
        
        self.tree_carrito.delete(selection[0])
        self.calcular_totales()
    
    def vaciar_carrito(self):
        """Vaciar todo el carrito"""
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        self.calcular_totales()
    
    def calcular_totales(self):
        """Calcular subtotal, IVA y total"""
        subtotal = 0
        
        for item in self.tree_carrito.get_children():
            item_data = self.tree_carrito.item(item)
            total_str = item_data['values'][3]
            total = float(total_str.replace('$', '').replace(',', ''))
            subtotal += total
        
        iva = subtotal * Config.IVA_PORCENTAJE
        total = subtotal + iva
        
        self.label_subtotal.config(text=f"${subtotal:,.0f}")
        self.label_iva.config(text=f"${iva:,.0f}")
        self.label_total.config(text=f"${total:,.0f}")
    
    def finalizar_venta(self):
        """Finalizar la venta actual"""
        if not self.tree_carrito.get_children():
            messagebox.showwarning("Advertencia", "Carrito vacío")
            return
        
        # Obtener total
        total = float(self.label_total.cget('text').replace('$', '').replace(',', ''))
        
        # Diálogo simple para confirmar
        respuesta = messagebox.askyesno("Confirmar Venta", 
                                       f"¿Confirmar venta por ${total:,.0f}?")
        
        if respuesta:
            try:
                # Generar folio
                fecha = datetime.now().strftime("%Y%m%d")
                self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha_venta) = DATE('now')")
                numero = self.cursor.fetchone()[0] + 1
                folio = f"VTA-{fecha}-{numero:04d}"
                
                # Calcular subtotal e IVA
                subtotal = float(self.label_subtotal.cget('text').replace('$', '').replace(',', ''))
                iva = float(self.label_iva.cget('text').replace('$', '').replace(',', ''))
                
                # Insertar venta
                self.cursor.execute('''
                    INSERT INTO ventas (numero_folio, subtotal, iva, total, metodo_pago)
                    VALUES (?, ?, ?, ?, ?)
                ''', (folio, subtotal, iva, total, 'efectivo'))
                
                venta_id = self.cursor.lastrowid
                
                # Insertar detalles y actualizar stock
                for item in self.tree_carrito.get_children():
                    item_data = self.tree_carrito.item(item)
                    producto_nombre = item_data['values'][0]
                    cantidad = item_data['values'][1]
                    precio = float(item_data['values'][2].replace('$', '').replace(',', ''))
                    
                    # Obtener ID del producto
                    self.cursor.execute("SELECT id FROM productos WHERE nombre = ?", (producto_nombre,))
                    producto = self.cursor.fetchone()
                    
                    if producto:
                        # Insertar detalle
                        self.cursor.execute('''
                            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, total_linea)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (venta_id, producto['id'], cantidad, precio, cantidad * precio))
                        
                        # Actualizar stock
                        self.cursor.execute('''
                            UPDATE productos SET stock = stock - ? WHERE id = ?
                        ''', (cantidad, producto['id']))
                
                self.conn.commit()
                
                messagebox.showinfo("Éxito", 
                                   f"✅ Venta realizada\nFolio: {folio}\nTotal: ${total:,.0f}")
                
                # Limpiar y actualizar
                self.vaciar_carrito()
                self.buscar_productos_venta()
                self.cargar_productos()
                self.actualizar_reportes()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar la venta: {e}")
    
    # ========== MÉTODOS PARA REPORTES ==========
    
    def actualizar_reportes(self):
        """Actualizar todos los reportes"""
        try:
            # Total productos
            self.cursor.execute("SELECT COUNT(*) FROM productos")
            total_p = self.cursor.fetchone()[0]
            self.label_total_productos.config(text=f"Total Productos: {total_p}")
            
            # Productos con stock bajo
            self.cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
            bajo = self.cursor.fetchone()[0]
            self.label_productos_bajo.config(text=f"Productos con Stock Bajo: {bajo}")
            
            # Total clientes
            self.cursor.execute("SELECT COUNT(*) FROM clientes")
            total_c = self.cursor.fetchone()[0]
            self.label_total_clientes.config(text=f"Total Clientes: {total_c}")
            
            # Ventas hoy
            self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha_venta) = DATE('now')")
            ventas_hoy = self.cursor.fetchone()[0]
            self.label_ventas_hoy.config(text=f"Ventas Hoy: {ventas_hoy}")
            
            # Actualizar barra de estado
            self.status_bar.config(text=f"Don Willy Ferretería | Productos: {total_p} | Clientes: {total_c} | Ventas hoy: {ventas_hoy}")
            
        except Exception as e:
            print(f"Error al actualizar reportes: {e}")

def main():
    """Función principal"""
    root = tk.Tk()
    app = SistemaFerreteriaGUI(root)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    main()