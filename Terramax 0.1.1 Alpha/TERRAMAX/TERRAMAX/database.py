import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="terramax.db"):
        # Asegurar que la base de datos se cree en la carpeta TERRAMAX
        terramax_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(terramax_dir, db_path)
        print(f"Inicializando base de datos en: {self.db_path}")
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
        self.migrate_database()
    
    def connect(self):
        """Establecer conexión con la base de datos"""
        try:
            print(f"Intentando conectar a la base de datos: {self.db_path}")
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print("Conexión establecida exitosamente")
        except Exception as e:
            print(f"Error al conectar a la base de datos: {str(e)}")
            raise e
    
    def close(self):
        """Cerrar la conexión con la base de datos"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Crear las tablas necesarias si no existen"""
        try:
            # Crear tabla de animales si no existe
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT NOT NULL,
                gender TEXT NOT NULL,
                age INTEGER NOT NULL,
                health_status TEXT NOT NULL,
                weight REAL,
                feeding_type TEXT,
                father_id INTEGER,
                mother_id INTEGER,
                medical_history TEXT,
                image_path TEXT,
                birth_date TEXT NOT NULL,
                added_date TEXT NOT NULL,
                FOREIGN KEY (father_id) REFERENCES animals (id),
                FOREIGN KEY (mother_id) REFERENCES animals (id)
            )
            ''')
            
            # Verificar si la tabla de vacunaciones ya existe
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vaccinations'")
            table_exists = self.cursor.fetchone() is not None
            
            if not table_exists:
                # Crear tabla de vacunaciones si no existe
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vaccinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL,
                    vaccine_type TEXT NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    applied_date TEXT,
                    status TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (animal_id) REFERENCES animals (id)
                )
                ''')
                print("Tabla vaccinations creada correctamente")
            else:
                # Verificar si necesitamos añadir las columnas status y notes
                try:
                    self.cursor.execute('PRAGMA table_info(vaccinations)')
                    columns = {row[1] for row in self.cursor.fetchall()}
                    
                    # Añadir columna status si no existe
                    if 'status' not in columns:
                        self.cursor.execute('ALTER TABLE vaccinations ADD COLUMN status TEXT')
                        print("Columna status añadida a vaccinations")
                    
                    # Añadir columna notes si no existe
                    if 'notes' not in columns:
                        self.cursor.execute('ALTER TABLE vaccinations ADD COLUMN notes TEXT')
                        print("Columna notes añadida a vaccinations")
                except Exception as e:
                    print(f"Error al verificar/añadir columnas a vaccinations: {str(e)}")
            
            # Crear tabla de tratamientos si no existe
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER NOT NULL,
                treatment_type TEXT NOT NULL,
                medication TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                responsible TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (animal_id) REFERENCES animals (id)
            )
            ''')
            
            # Crear tabla de alimentación
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeding (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id INTEGER,
                feed_type TEXT NOT NULL,
                amount REAL,
                unit TEXT,
                date TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (animal_id) REFERENCES animals (id)
            )
            ''')
            
            # Crear tabla de eventos del calendario
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_date TEXT NOT NULL,
                title TEXT,
                description TEXT,
                entity_id INTEGER,
                entity_type TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            self.conn.commit()
            print("Todas las tablas verificadas/creadas exitosamente")
            
        except Exception as e:
            print(f"Error al crear/verificar las tablas: {str(e)}")
            self.conn.rollback()
    
    def migrate_database(self):
        """Realizar migraciones necesarias para actualizar la estructura de la base de datos"""
        try:
            print("Verificando si es necesario migrar la base de datos...")
            
            # Verificar si la tabla vaccinations necesita ser actualizada
            self.cursor.execute("PRAGMA table_info(vaccinations)")
            columns = {row[1] for row in self.cursor.fetchall()}
            
            # Agregar columnas faltantes
            if "status" not in columns:
                print("Agregando columna 'status' a la tabla vaccinations")
                self.cursor.execute("ALTER TABLE vaccinations ADD COLUMN status TEXT DEFAULT 'Pendiente'")
            
            if "notes" not in columns:
                print("Agregando columna 'notes' a la tabla vaccinations")
                self.cursor.execute("ALTER TABLE vaccinations ADD COLUMN notes TEXT")
            
            if "applied_date" not in columns:
                print("Agregando columna 'applied_date' a la tabla vaccinations")
                self.cursor.execute("ALTER TABLE vaccinations ADD COLUMN applied_date TEXT")
            
            # Verificar si hay vacunaciones sin status y actualizarlas
            self.cursor.execute("UPDATE vaccinations SET status = 'Pendiente' WHERE status IS NULL OR status = ''")
            
            self.conn.commit()
            print("Migración de base de datos completada correctamente")
        except Exception as e:
            print(f"Error durante la migración de la base de datos: {str(e)}")
            self.conn.rollback()
    
    # Métodos para animales
    def add_animal(self, animal_data):
        """Agregar un nuevo animal a la base de datos"""
        query = '''
        INSERT INTO animals (
            name, species, breed, gender, age, health_status,
            weight, feeding_type, father_id, mother_id, medical_history, image_path, birth_date, added_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            print(f"Intentando insertar animal con datos: {animal_data}")  # Debug
            self.cursor.execute(query, (
                animal_data['name'],
                animal_data['species'],
                animal_data['breed'],
                animal_data['gender'],
                animal_data['age'],
                animal_data['health_status'],
                animal_data.get('weight'),
                animal_data.get('feeding_type'),
                animal_data.get('father_id'),
                animal_data.get('mother_id'),
                animal_data.get('medical_history'),
                animal_data.get('image_path'),
                animal_data['birth_date'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            self.conn.commit()
            print(f"Animal insertado exitosamente con ID: {self.cursor.lastrowid}")  # Debug
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error al insertar animal: {str(e)}")  # Debug
            self.conn.rollback()
            raise
    
    def get_animals(self):
        """Obtener todos los animales"""
        self.cursor.execute('SELECT * FROM animals ORDER BY added_date DESC')
        return self.cursor.fetchall()
    
    def get_animal(self, animal_id):
        """Obtener un animal por su ID"""
        try:
            print(f"Intentando obtener animal con ID: {animal_id}")  # Debug
            print(f"Tipo de ID recibido: {type(animal_id)}")  # Debug
            
            # Asegurar que el ID sea un entero
            try:
                animal_id = int(animal_id)
                print(f"ID convertido a entero: {animal_id}")  # Debug
            except (TypeError, ValueError) as e:
                print(f"Error al convertir ID a entero: {str(e)}")  # Debug
                return None
            
            query = """
                SELECT 
                    id,             -- 0
                    name,           -- 1
                    species,        -- 2
                    breed,          -- 3
                    gender,         -- 4
                    age,            -- 5
                    health_status,  -- 6
                    weight,         -- 7
                    feeding_type,   -- 8
                    father_id,      -- 9
                    mother_id,      -- 10
                    medical_history,-- 11
                    image_path,     -- 12
                    birth_date,     -- 13
                    added_date      -- 14
                FROM animals 
                WHERE id = ?
            """
            print(f"Ejecutando query: {query}")  # Debug
            print(f"Con parámetro: {animal_id}")  # Debug
            
            # Verificar si la conexión está activa
            if not self.conn:
                print("La conexión a la base de datos no está activa. Reconectando...")  # Debug
                self.connect()
            
            # Asegurar que tenemos un cursor válido
            if not self.cursor:
                print("El cursor no es válido. Creando uno nuevo...")  # Debug
                self.cursor = self.conn.cursor()
            
            self.cursor.execute(query, (animal_id,))
            animal = self.cursor.fetchone()
            
            print(f"Resultado de la consulta: {animal}")  # Debug
            if animal is None:
                print(f"No se encontró ningún animal con ID: {animal_id}")  # Debug
            else:
                print(f"Animal encontrado. Longitud de datos: {len(animal)}")  # Debug
                print(f"Datos del animal: {dict(zip(['id', 'name', 'species', 'breed', 'gender', 'age', 'health_status', 'weight', 'feeding_type', 'father_id', 'mother_id', 'medical_history', 'image_path', 'birth_date', 'added_date'], animal))}")  # Debug
            
            return animal
            
        except sqlite3.Error as e:
            print(f"Error de SQLite: {str(e)}")  # Debug
            print(f"Traza completa del error:", e.__traceback__)
            return None
        except Exception as e:
            print(f"Error al obtener animal: {str(e)}")  # Debug
            print(f"Traza completa del error:", e.__traceback__)
            return None
    
    def update_animal(self, animal_id, animal_data):
        """Actualizar datos de un animal"""
        query = '''
        UPDATE animals 
        SET name = ?, species = ?, breed = ?, gender = ?, age = ?,
            health_status = ?, weight = ?, feeding_type = ?, father_id = ?, mother_id = ?,
            medical_history = ?, image_path = ?, birth_date = ?
        WHERE id = ?
        '''
        try:
            print(f"Intentando actualizar animal {animal_id} con datos: {animal_data}")  # Debug
            self.cursor.execute(query, (
                animal_data['name'],
                animal_data['species'],
                animal_data['breed'],
                animal_data['gender'],
                animal_data['age'],
                animal_data['health_status'],
                animal_data.get('weight'),
                animal_data.get('feeding_type'),
                animal_data.get('father_id'),
                animal_data.get('mother_id'),
                animal_data.get('medical_history'),
                animal_data.get('image_path'),
                animal_data['birth_date'],
                animal_id
            ))
            self.conn.commit()
            print(f"Animal {animal_id} actualizado exitosamente")  # Debug
        except Exception as e:
            print(f"Error al actualizar animal: {str(e)}")  # Debug
            self.conn.rollback()
            raise
    
    def delete_animal(self, animal_id):
        """Eliminar un animal"""
        self.cursor.execute('DELETE FROM animals WHERE id = ?', (animal_id,))
        self.conn.commit()
    
    # Métodos para vacunas
    def add_vaccination(self, vaccination_data):
        """Agregar una nueva vacuna"""
        try:
            # Determinar las columnas existentes en la tabla vaccinations
            self.cursor.execute("PRAGMA table_info(vaccinations)")
            columns = [row[1] for row in self.cursor.fetchall()]
            print(f"Columnas existentes en la tabla vaccinations: {columns}")
            
            # Preparar la consulta basada en las columnas existentes
            column_names = []
            placeholders = []
            values = []
            
            # Columnas obligatorias
            if "animal_id" in columns:
                column_names.append("animal_id")
                placeholders.append("?")
                values.append(vaccination_data['animal_id'])
                
            if "vaccine_type" in columns:
                column_names.append("vaccine_type")
                placeholders.append("?")
                values.append(vaccination_data['vaccine_type'])
                
            if "scheduled_date" in columns:
                column_names.append("scheduled_date")
                placeholders.append("?")
                values.append(vaccination_data['scheduled_date'])
                
            # Columnas opcionales
            if "status" in columns:
                column_names.append("status")
                placeholders.append("?")
                values.append(vaccination_data.get('status', 'Pendiente'))
                
            if "notes" in columns:
                column_names.append("notes")
                placeholders.append("?")
                values.append(vaccination_data.get('notes', None))
                
            if "created_at" in columns:
                column_names.append("created_at")
                placeholders.append("?")
                values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
            if "updated_at" in columns:
                column_names.append("updated_at")
                placeholders.append("?")
                values.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
            if "applied_date" in columns:
                column_names.append("applied_date")
                placeholders.append("?")
                values.append(vaccination_data.get('applied_date', None))
            
            # Construir y ejecutar la consulta
            if not column_names:
                raise Exception("No se encontraron columnas válidas en la tabla vaccinations")
                
            query = f"INSERT INTO vaccinations ({', '.join(column_names)}) VALUES ({', '.join(placeholders)})"
            
            print(f"Ejecutando query: {query}")
            print(f"Con parámetros: {values}")
            
            self.cursor.execute(query, values)
            self.conn.commit()
            
            vaccination_id = self.cursor.lastrowid
            print(f"Vacunación guardada con ID: {vaccination_id}")
            
            return vaccination_id
        except Exception as e:
            print(f"Error al guardar la vacunación: {str(e)}")
            self.conn.rollback()
            raise
    
    def get_vaccinations(self, id=None, animal_id=None, scheduled_date=None, status=None):
        """Obtener vacunaciones con filtros opcionales"""
        try:
            # Verificar si la tabla existe
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vaccinations'")
            if not self.cursor.fetchone():
                print("La tabla vaccinations no existe")
                return []
            
            # Verificar las columnas que existen
            self.cursor.execute("PRAGMA table_info(vaccinations)")
            columns_info = self.cursor.fetchall()
            columns = [row[1] for row in columns_info]
            print(f"Columnas en la tabla vaccinations: {columns}")
            
            # Verificar también la tabla animals
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='animals'")
            if not self.cursor.fetchone():
                print("La tabla animals no existe")
                return []
                
            self.cursor.execute("PRAGMA table_info(animals)")
            animal_columns = [row[1] for row in self.cursor.fetchall()]
            print(f"Columnas en la tabla animals: {animal_columns}")
            
            # Construir la consulta basada en las columnas disponibles
            select_columns = ["v.id"]
            
            if "animal_id" in columns:
                select_columns.append("v.animal_id")
            else:
                select_columns.append("NULL as animal_id")
                
            if "vaccine_type" in columns:
                select_columns.append("v.vaccine_type")
            else:
                select_columns.append("'Desconocido' as vaccine_type")
                
            if "scheduled_date" in columns:
                select_columns.append("v.scheduled_date")
            else:
                select_columns.append("NULL as scheduled_date")
                
            if "notes" in columns:
                select_columns.append("v.notes")
            else:
                select_columns.append("NULL as notes")
                
            if "status" in columns:
                select_columns.append("v.status")
            else:
                select_columns.append("'Pendiente' as status")
                
            if "applied_date" in columns:
                select_columns.append("v.applied_date")
            else:
                select_columns.append("NULL as applied_date")
            
            # Asegurar que siempre intentemos obtener el nombre del animal
            # Usar COALESCE para evitar valores nulos
            query = f"""
            SELECT {', '.join(select_columns)}, 
                   COALESCE(a.name, 'No encontrado') as animal_name
            FROM vaccinations v
            LEFT JOIN animals a ON v.animal_id = a.id
            """
            
            # Construir la cláusula WHERE
            conditions = []
            params = []
            
            if id is not None:
                conditions.append("v.id = ?")
                params.append(id)
                
            if animal_id is not None and "animal_id" in columns:
                conditions.append("v.animal_id = ?")
                params.append(animal_id)
                
            if scheduled_date is not None and "scheduled_date" in columns:
                conditions.append("v.scheduled_date = ?")
                params.append(scheduled_date)
                
            if status is not None and "status" in columns:
                conditions.append("v.status = ?")
                params.append(status)
                
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Ordenar por fecha programada si existe
            if "scheduled_date" in columns:
                query += " ORDER BY v.scheduled_date DESC"
            
            print(f"Ejecutando consulta: {query}")
            print(f"Con parámetros: {params}")
            
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            
            # Imprimir resultados para depuración
            print(f"Se encontraron {len(result)} vacunaciones")
            if result:
                print(f"Primera vacunación: {result[0]}")
                
            # Verificar longitud consistente de cada fila
            expected_length = 8  # id, animal_id, vaccine_type, scheduled_date, notes, status, applied_date, animal_name
            for i, row in enumerate(result):
                print(f"Vacunación {i+1}: {row}")
                if len(row) != expected_length:
                    print(f"ADVERTENCIA: La vacunación {i+1} tiene {len(row)} columnas en lugar de {expected_length}")
                
                # Verificar el nombre del animal
                animal_name = row[-1]  # Última columna es animal_name
                if animal_name is None or animal_name == "":
                    print(f"ADVERTENCIA: La vacunación {i+1} tiene un nombre de animal nulo o vacío")
                    # Intentar obtener el nombre del animal directamente
                    animal_id = row[1]  # Segunda columna es animal_id
                    if animal_id:
                        try:
                            self.cursor.execute("SELECT name FROM animals WHERE id = ?", (animal_id,))
                            animal_data = self.cursor.fetchone()
                            if animal_data:
                                print(f"Nombre de animal obtenido directamente: {animal_data[0]}")
                        except Exception as e:
                            print(f"Error al obtener nombre de animal: {str(e)}")
            
            return result
        except Exception as e:
            print(f"Error al obtener vacunaciones: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_animal_vaccinations(self, animal_id):
        """Obtener vacunas de un animal específico"""
        self.cursor.execute('''
        SELECT v.*, a.name as animal_name 
        FROM vaccinations v
        JOIN animals a ON v.animal_id = a.id
        WHERE v.animal_id = ?
        ORDER BY v.scheduled_date
        ''', (animal_id,))
        return self.cursor.fetchall()
    
    def update_vaccination(self, vaccination_id, data):
        """Actualizar una vacunación en la base de datos
        
        Args:
            vaccination_id: ID de la vacunación a actualizar
            data: Diccionario con los campos a actualizar
                animal_id: ID del animal (opcional)
                vaccine_type: Tipo de vacuna (opcional)
                scheduled_date: Fecha programada (opcional)
                notes: Notas (opcional)
                status: Estado (opcional)
        """
        try:
            # Determinar las columnas existentes en la tabla vaccinations
            self.cursor.execute("PRAGMA table_info(vaccinations)")
            columns = [row[1] for row in self.cursor.fetchall()]
            print(f"Columnas existentes en la tabla vaccinations: {columns}")
            
            # Crear la parte SET de la consulta SQL
            set_parts = []
            params = []
            
            if "animal_id" in data and "animal_id" in columns:
                set_parts.append("animal_id = ?")
                params.append(data["animal_id"])
            
            if "vaccine_type" in data and "vaccine_type" in columns:
                set_parts.append("vaccine_type = ?")
                params.append(data["vaccine_type"])
            
            if "scheduled_date" in data and "scheduled_date" in columns:
                set_parts.append("scheduled_date = ?")
                params.append(data["scheduled_date"])
            
            if "notes" in data and "notes" in columns:
                set_parts.append("notes = ?")
                params.append(data["notes"])
            
            if "status" in data and "status" in columns:
                set_parts.append("status = ?")
                params.append(data["status"])
                
            if "applied_date" in data and "applied_date" in columns:
                set_parts.append("applied_date = ?")
                params.append(data["applied_date"])
            
            # Actualizar la fecha de modificación si existe la columna
            if "updated_at" in columns:
                set_parts.append("updated_at = ?")
                params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Si no hay nada que actualizar, salir
            if not set_parts:
                return True
            
            # Construir la consulta SQL
            query = f"UPDATE vaccinations SET {', '.join(set_parts)} WHERE id = ?"
            params.append(vaccination_id)
            
            print(f"Ejecutando query de actualización: {query}")
            print(f"Con parámetros: {params}")
            
            # Ejecutar la consulta
            self.cursor.execute(query, params)
            self.conn.commit()
            
            print(f"Vacunación con ID {vaccination_id} actualizada correctamente")
            return True
        except Exception as e:
            print(f"Error actualizando vacunación: {str(e)}")
            return False
    
    # Métodos para tratamientos
    def add_treatment(self, treatment_data):
        """Agregar un nuevo tratamiento"""
        query = '''
        INSERT INTO treatments (animal_id, treatment_type, medication, start_date, end_date, status, responsible, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(query, (
            treatment_data['animal_id'],
            treatment_data['treatment_type'],
            treatment_data['medication'],
            treatment_data['start_date'],
            treatment_data['end_date'],
            treatment_data['status'],
            treatment_data['responsible'],
            treatment_data.get('notes', None)
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_treatments(self):
        """Obtener todos los tratamientos"""
        self.cursor.execute('''
        SELECT t.*, a.name as animal_name, a.species as animal_species
        FROM treatments t
        JOIN animals a ON t.animal_id = a.id
        ORDER BY t.start_date
        ''')
        return self.cursor.fetchall()
    
    def get_animal_treatments(self, animal_id):
        """Obtener tratamientos de un animal específico"""
        self.cursor.execute('''
        SELECT t.*, a.name as animal_name, a.species as animal_species
        FROM treatments t
        JOIN animals a ON t.animal_id = a.id
        WHERE t.animal_id = ?
        ORDER BY t.start_date
        ''', (animal_id,))
        return self.cursor.fetchall()
    
    def update_treatment(self, treatment_id, treatment_data):
        """Actualizar datos de un tratamiento"""
        query = '''
        UPDATE treatments 
        SET treatment_type = ?, medication = ?, start_date = ?, end_date = ?, status = ?, responsible = ?, notes = ?
        WHERE id = ?
        '''
        self.cursor.execute(query, (
            treatment_data['treatment_type'],
            treatment_data['medication'],
            treatment_data['start_date'],
            treatment_data['end_date'],
            treatment_data['status'],
            treatment_data['responsible'],
            treatment_data.get('notes', None),
            treatment_id
        ))
        self.conn.commit()
    
    def delete_treatment(self, treatment_id):
        """Eliminar un tratamiento"""
        self.cursor.execute('DELETE FROM treatments WHERE id = ?', (treatment_id,))
        self.conn.commit()

    def get_calendar_events(self):
        """Obtener eventos para el calendario"""
        try:
            print("Obteniendo eventos para el calendario...")
            # Verificar si existe la tabla vaccinations
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vaccinations'")
            table_exists = self.cursor.fetchone() is not None
            
            if not table_exists:
                print("La tabla vaccinations no existe")
                return {}
                
            # Verificar las columnas que existen en la tabla
            self.cursor.execute("PRAGMA table_info(vaccinations)")
            columns = {row[1] for row in self.cursor.fetchall()}
            
            # Construir la consulta dependiendo de las columnas disponibles
            query = "SELECT scheduled_date, COUNT(*) as count FROM vaccinations"
            
            # En lugar de filtrar por estado, mostrar todos los eventos
            # Pero asegurarse de que la fecha no sea NULL
            if "scheduled_date" in columns:
                query += " WHERE scheduled_date IS NOT NULL"
                
            query += " GROUP BY scheduled_date"
            
            print(f"Ejecutando consulta de eventos del calendario: {query}")
            
            self.cursor.execute(query)
            events = {}
            for row in self.cursor.fetchall():
                if row[0]:  # Asegurarse de que la fecha no sea None
                    events[row[0]] = row[1]
            
            print(f"Eventos encontrados: {events}")
            return events
        except Exception as e:
            print(f"Error al obtener eventos del calendario: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def repair_database(self):
        """Realiza mantenimiento y reparación de la base de datos"""
        try:
            print("Iniciando reparación de la base de datos...")
            
            # 1. Verificar integridad de la base de datos
            print("Verificando integridad de la base de datos...")
            self.cursor.execute("PRAGMA integrity_check")
            integrity_result = self.cursor.fetchone()[0]
            if integrity_result != "ok":
                print(f"ADVERTENCIA: Problemas de integridad detectados: {integrity_result}")
            else:
                print("Integridad de la base de datos: OK")
                
            # 2. Reparar tabla de vacunaciones si existe
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vaccinations'")
            if self.cursor.fetchone():
                print("Reparando tabla vaccinations...")
                
                # 2.1 Verificar columnas existentes
                self.cursor.execute("PRAGMA table_info(vaccinations)")
                columns = {row[1] for row in self.cursor.fetchall()}
                print(f"Columnas existentes: {columns}")
                
                # 2.2 Asegurar que existan las columnas necesarias
                for column, type_default in [
                    ("animal_id", "INTEGER"),
                    ("vaccine_type", "TEXT"),
                    ("scheduled_date", "TEXT"),
                    ("status", "TEXT DEFAULT 'Pendiente'"),
                    ("notes", "TEXT"),
                    ("applied_date", "TEXT")
                ]:
                    if column not in columns:
                        print(f"Agregando columna faltante: {column}")
                        self.cursor.execute(f"ALTER TABLE vaccinations ADD COLUMN {column} {type_default}")
                
                # 2.3 Corregir datos inválidos 
                # Establecer estado pendiente donde sea nulo
                self.cursor.execute("UPDATE vaccinations SET status = 'Pendiente' WHERE status IS NULL OR status = ''")
                
                # 2.4 Verifica si hay registros de vacunación y corrige cualquier anomalía
                self.cursor.execute("SELECT id, animal_id, vaccine_type, scheduled_date FROM vaccinations")
                rows = self.cursor.fetchall()
                print(f"Verificando {len(rows)} registros de vacunación...")
                
                for row in rows:
                    vac_id, animal_id, vaccine_type, scheduled_date = row
                    problems = []
                    
                    # Verificar animal_id
                    if animal_id is None:
                        problems.append("animal_id es NULL")
                    else:
                        self.cursor.execute("SELECT id FROM animals WHERE id = ?", (animal_id,))
                        if not self.cursor.fetchone():
                            problems.append(f"animal_id {animal_id} no existe")
                    
                    # Verificar vaccine_type
                    if not vaccine_type:
                        problems.append("vaccine_type es NULL o vacío")
                        self.cursor.execute("UPDATE vaccinations SET vaccine_type = 'Sin especificar' WHERE id = ?", (vac_id,))
                    
                    # Verificar scheduled_date
                    if not scheduled_date:
                        problems.append("scheduled_date es NULL o vacío")
                    
                    if problems:
                        print(f"ADVERTENCIA: Registro de vacunación ID {vac_id} tiene problemas: {', '.join(problems)}")
                
                print("Reparación de tabla vaccinations completada")
            else:
                print("La tabla vaccinations no existe, creándola...")
                self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS vaccinations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    animal_id INTEGER NOT NULL,
                    vaccine_type TEXT NOT NULL,
                    scheduled_date TEXT NOT NULL,
                    applied_date TEXT,
                    status TEXT NOT NULL DEFAULT 'Pendiente',
                    notes TEXT,
                    FOREIGN KEY (animal_id) REFERENCES animals (id)
                )
                ''')
            
            # 3. Ejecutar VACUUM para optimizar la base de datos
            print("Optimizando la base de datos...")
            self.conn.execute("VACUUM")
            
            # 4. Confirmar cambios
            self.conn.commit()
            print("Reparación de la base de datos completada exitosamente")
            return True
        
        except Exception as e:
            print(f"Error durante la reparación de la base de datos: {str(e)}")
            import traceback
            traceback.print_exc()
            self.conn.rollback()
            return False