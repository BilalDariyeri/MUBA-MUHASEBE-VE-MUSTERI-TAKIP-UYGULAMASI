"""
Logging Service - İşlem geçmişi kayıt servisi
"""
from sql_init import get_db
from typing import Dict, Optional, List
import uuid
from datetime import datetime


class LoggingService:
    """İşlem geçmişi kayıt servisi"""
    
    def __init__(self):
        self.db = get_db()
        self.table_name = 'activity_logs'
    
    def log(self, user_id: Optional[str], action: str, entity_type: Optional[str] = None, 
            entity_id: Optional[str] = None, details: Optional[Dict] = None, ip_address: Optional[str] = None):
        """İşlem kaydı oluştur"""
        try:
            log_id = str(uuid.uuid4())
            details_json = None
            if details:
                import json
                details_json = json.dumps(details, ensure_ascii=False)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    INSERT INTO {self.table_name} 
                    (id, user_id, action, entity_type, entity_id, details, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id,
                    user_id,
                    action,
                    entity_type,
                    entity_id,
                    details_json,
                    ip_address
                ))
            return log_id
        except Exception as e:
            print(f"Log kayıt hatası: {e}")
            return None
    
    def get_logs(self, user_id: Optional[str] = None, entity_type: Optional[str] = None,
                 action: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """İşlem kayıtlarını getir"""
        try:
            conditions = []
            params = []
            
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            if entity_type:
                conditions.append("entity_type = ?")
                params.append(entity_type)
            
            if action:
                conditions.append("action = ?")
                params.append(action)
            
            where_clause = ""
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)
            
            params.append(limit)
            
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ?
                """, params)
                rows = cursor.fetchall()
                logs = []
                for row in rows:
                    log_data = dict(row)
                    if log_data.get('details'):
                        import json
                        try:
                            log_data['details'] = json.loads(log_data['details'])
                        except:
                            pass
                    logs.append(log_data)
                return logs
        except Exception as e:
            raise Exception(f"Log getirme hatası: {str(e)}")
    
    def get_user_logs(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Kullanıcıya ait işlem kayıtlarını getir"""
        return self.get_logs(user_id=user_id, limit=limit)
    
    def get_entity_logs(self, entity_type: str, entity_id: str, limit: int = 50) -> List[Dict]:
        """Belirli bir entity'ye ait işlem kayıtlarını getir"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"""
                    SELECT * FROM {self.table_name}
                    WHERE entity_type = ? AND entity_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (entity_type, entity_id, limit))
                rows = cursor.fetchall()
                logs = []
                for row in rows:
                    log_data = dict(row)
                    if log_data.get('details'):
                        import json
                        try:
                            log_data['details'] = json.loads(log_data['details'])
                        except:
                            pass
                    logs.append(log_data)
                return logs
        except Exception as e:
            raise Exception(f"Entity log getirme hatası: {str(e)}")
    
    def delete_log(self, log_id: str) -> bool:
        """Tek bir log kaydını sil"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (log_id,))
                return cursor.rowcount > 0
        except Exception as e:
            raise Exception(f"Log silme hatası: {str(e)}")
    
    def delete_logs(self, log_ids: List[str]) -> int:
        """Birden fazla log kaydını sil"""
        try:
            if not log_ids:
                return 0
            
            placeholders = ','.join(['?'] * len(log_ids))
            with self.db.get_cursor() as cursor:
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id IN ({placeholders})", log_ids)
                return cursor.rowcount
        except Exception as e:
            raise Exception(f"Log silme hatası: {str(e)}")
    
    def delete_all_logs(self) -> int:
        """Tüm log kayıtlarını sil (DİKKATLİ KULLANIN!)"""
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) as count FROM {self.table_name}")
                count = cursor.fetchone()['count']
                cursor.execute(f"DELETE FROM {self.table_name}")
                return count
        except Exception as e:
            raise Exception(f"Tüm logları silme hatası: {str(e)}")

