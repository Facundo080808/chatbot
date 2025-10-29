from db import supabase
from datetime import datetime
def getOrCreateClient(nombre, celular):
    try:
        # Buscar si ya existe por celular
        res = supabase.table("Clientes").select("*").eq("celular", celular).execute()
        if res.data:
            print(f"🔍 Cliente encontrado: {res.data[0]}")
            return res.data[0]["id"]

        # Crear nuevo si no existe
        nuevo = supabase.table("Clientes").insert({
            "nombre": nombre,
            "celular": celular
        }).execute()
        print(f"➕ Nuevo cliente creado: {nuevo.data[0]}")
        return nuevo.data[0]["id"]
    except Exception as e:
        print(f"❌ Error al obtener/crear cliente: {e}")
        return None
#traer todos los clientes
def getClients():
    try:
        res = supabase.table("Clientes").select("*").execute()
        print("📋 Clientes obtenidos:", res.data)
        return res.data
    except Exception as e:
        print(f"❌ Error al obtener clientes: {e}")
        return []
def shiftOccupied(dia, hora):
    #"""Verifica si un turno ya está reservado."""
    try:
        res = supabase.table("turnos").select("*").eq("dia", dia).eq("hora", hora).execute()
        return len(res.data) > 0
    except Exception as e:
        print(f"❌ Error al verificar turno: {e}")
        return False

#traer todos los turnos
def getShifts():
    hoy = datetime.today().isoformat()
    try:
        res = supabase.table("turnos") \
        .select("id_turno, dia, hora, Clientes(nombre, celular)") \
        .gte("dia", hoy) \
        .order("dia", desc=False) \
        .execute()
        print("📋 Turnos obtenidos:", res.data)
        return res.data
    except Exception as e:
        print(f"❌ Error al obtener turnos: {e}")
        return []

def createShift(nombre, celular, dia, hora):
  
    try:
        cliente_id = getOrCreateClient(nombre, celular)
        if not cliente_id:
            print("⚠️ No se pudo obtener cliente_id.")
            return

        supabase.table("turnos").insert({
            "dia": dia,
            "hora": hora,
            "id_Cliente": cliente_id
        }).execute()

        print(f"💾 Turno guardado correctamente: {nombre} -> {dia} {hora}")
    except Exception as e:
        print(f"❌ Error al guardar turno: {e}")
