from supabase import create_client, Client
import config as config

supabase: Client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
