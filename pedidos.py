from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import os

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- CONEXIÓN A SUPABASE ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FUNCIÓN PARA CREAR PEDIDO ---
def crear_pedido(nombre_cliente: str, pedido: str, domicilio: str ):
    """
    Inserta un nuevo pedido en la tabla 'pedidos'.
    """
    try:
        fecha_actual = datetime.now().isoformat()

        data = {
            "nombre_cliente": nombre_cliente,
            "pedido": pedido,
            "fecha": fecha_actual,
            "Domicilio": domicilio
        }

        response = supabase.table("pedidos").insert(data).execute()

        if response.data:
            print("✅ Pedido creado correctamente en Supabase.")
            return response.data[0]
        else:
            print("⚠️ No se pudo insertar el pedido.")
            return None

    except Exception as e:
        print("❌ Error al crear el pedido:", e)
        return None

