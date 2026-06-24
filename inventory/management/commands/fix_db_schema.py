from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes database schema inconsistencies by adding missing columns to PostgreSQL tables'

    def handle(self, *args, **options):
        db_vendor = connection.vendor
        self.stdout.write(self.style.WARNING(f"Database engine vendor: {db_vendor}"))
        
        if db_vendor != 'postgresql':
            self.stdout.write(self.style.SUCCESS("Database is not PostgreSQL. Skipping schema fixes."))
            return

        with connection.cursor() as cursor:
            # Helper to check if column exists
            def column_exists(table, column):
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s;
                """, [table, column])
                return cursor.fetchone()[0] > 0

            # Helper to check column nullability
            def is_nullable(table, column):
                cursor.execute("""
                    SELECT is_nullable 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND column_name = %s;
                """, [table, column])
                res = cursor.fetchone()
                return res[0] == 'YES' if res else True

            # Helper to check if constraint exists
            def constraint_exists(table, constraint):
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.table_constraints 
                    WHERE table_name = %s AND constraint_name = %s;
                """, [table, constraint])
                return cursor.fetchone()[0] > 0

            # Helper to execute sql and catch errors
            def execute_sql(sql):
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS(f"Executed: {sql}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error executing {sql}: {e}"))

            # 1. Fix inventory_equipment
            self.stdout.write("Checking inventory_equipment...")
            if not column_exists('inventory_equipment', 'ba'):
                execute_sql("ALTER TABLE inventory_equipment ADD COLUMN ba character varying(100) NULL;")
            if not column_exists('inventory_equipment', 'make'):
                execute_sql("ALTER TABLE inventory_equipment ADD COLUMN make character varying(100) NULL;")
            if not column_exists('inventory_equipment', 'model_no'):
                execute_sql("ALTER TABLE inventory_equipment ADD COLUMN model_no character varying(100) NULL;")
                
            for col in ['remarks', 'uplink_connectivity', 'total_ports']:
                if column_exists('inventory_equipment', col) and not is_nullable('inventory_equipment', col):
                    execute_sql(f"ALTER TABLE inventory_equipment ALTER COLUMN {col} DROP NOT NULL;")

            # 2. Fix inventory_ebcircuit
            self.stdout.write("Checking inventory_ebcircuit...")
            eb_cols = {
                'a_address': 'text NULL',
                'a_media': 'character varying(100) NULL',
                'cable_data': 'character varying(255) NULL',
                'lc_id': 'character varying(100) NULL',
                'node_at_a_end': 'character varying(100) NULL',
                'node_at_b_end': 'character varying(100) NULL',
                'port_b_side': 'character varying(100) NULL',
                'status': 'character varying(100) NULL',
                'working_status': 'character varying(100) NULL',
            }
            for col, col_type in eb_cols.items():
                if not column_exists('inventory_ebcircuit', col):
                    execute_sql(f"ALTER TABLE inventory_ebcircuit ADD COLUMN {col} {col_type};")

            for col in ['bandwidth', 'circuit_type', 'client_name', 'customer_end_node', 'fiber_mode', 'te_id']:
                if column_exists('inventory_ebcircuit', col) and not is_nullable('inventory_ebcircuit', col):
                    execute_sql(f"ALTER TABLE inventory_ebcircuit ALTER COLUMN {col} DROP NOT NULL;")

            # 3. Fix inventory_mobilebts
            self.stdout.write("Checking inventory_mobilebts...")
            if not column_exists('inventory_mobilebts', 'backhaul_media'):
                execute_sql("ALTER TABLE inventory_mobilebts ADD COLUMN backhaul_media character varying(100) NULL;")
            if not column_exists('inventory_mobilebts', 'connected_equipment'):
                execute_sql("ALTER TABLE inventory_mobilebts ADD COLUMN connected_equipment character varying(255) NULL;")
            if not column_exists('inventory_mobilebts', 'non_4g_type'):
                execute_sql("ALTER TABLE inventory_mobilebts ADD COLUMN non_4g_type character varying(50) NULL;")
            if not column_exists('inventory_mobilebts', 'site_type'):
                execute_sql("ALTER TABLE inventory_mobilebts ADD COLUMN site_type character varying(20) NOT NULL DEFAULT '4G';")
            if not column_exists('inventory_mobilebts', 'te_id'):
                execute_sql("ALTER TABLE inventory_mobilebts ADD COLUMN te_id integer NULL;")
            
            if not constraint_exists('inventory_mobilebts', 'fk_inventory_mobilebts_te_id'):
                execute_sql("""
                    ALTER TABLE inventory_mobilebts 
                    ADD CONSTRAINT fk_inventory_mobilebts_te_id 
                    FOREIGN KEY (te_id) REFERENCES inventory_telephoneexchange (id) 
                    ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;
                """)

            self.stdout.write(self.style.SUCCESS("Database schema check and fix completed successfully."))
