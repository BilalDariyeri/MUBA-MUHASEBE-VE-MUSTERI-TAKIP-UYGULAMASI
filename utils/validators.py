"""
Validators - Form validasyon yardımcıları
"""
import re
from datetime import datetime
from typing import Optional, Tuple


class Validators:
    """Form validasyon sınıfı"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """E-posta validasyonu"""
        if not email or not email.strip():
            return False, "E-posta adresi gereklidir"
        
        email = email.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Geçerli bir e-posta adresi giriniz"
        
        return True, None
    
    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Telefon validasyonu"""
        if not phone:
            return True, None  # Opsiyonel
        
        phone = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if len(phone) < 10:
            return False, "Geçerli bir telefon numarası giriniz"
        
        if not phone.isdigit():
            return False, "Telefon numarası sadece rakam içermelidir"
        
        return True, None
    
    @staticmethod
    def validate_tax_number(tax_no: str) -> Tuple[bool, Optional[str]]:
        """Vergi numarası validasyonu"""
        if not tax_no or not tax_no.strip():
            return False, "Vergi numarası gereklidir"
        
        tax_no = tax_no.strip().replace(' ', '')
        if len(tax_no) != 10 and len(tax_no) != 11:
            return False, "Vergi numarası 10 veya 11 haneli olmalıdır"
        
        if not tax_no.isdigit():
            return False, "Vergi numarası sadece rakam içermelidir"
        
        return True, None
    
    @staticmethod
    def validate_date(date_str: str, format_str: str = "%Y-%m-%d") -> Tuple[bool, Optional[str], Optional[datetime]]:
        """Tarih validasyonu"""
        if not date_str or not date_str.strip():
            return False, "Tarih gereklidir", None
        
        try:
            date_obj = datetime.strptime(date_str.strip(), format_str)
            return True, None, date_obj
        except ValueError:
            return False, f"Tarih formatı geçersiz. Beklenen format: {format_str}", None
    
    @staticmethod
    def validate_required(value: any, field_name: str) -> Tuple[bool, Optional[str]]:
        """Zorunlu alan validasyonu"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name} gereklidir"
        return True, None
    
    @staticmethod
    def validate_number(value: any, field_name: str, min_value: Optional[float] = None, 
                       max_value: Optional[float] = None) -> Tuple[bool, Optional[str]]:
        """Sayı validasyonu"""
        if value is None or value == '':
            return False, f"{field_name} gereklidir"
        
        try:
            num_value = float(value)
            if min_value is not None and num_value < min_value:
                return False, f"{field_name} en az {min_value} olmalıdır"
            if max_value is not None and num_value > max_value:
                return False, f"{field_name} en fazla {max_value} olmalıdır"
            return True, None
        except (ValueError, TypeError):
            return False, f"{field_name} geçerli bir sayı olmalıdır"
    
    @staticmethod
    def validate_password(password: str, min_length: int = 6) -> Tuple[bool, Optional[str]]:
        """Şifre validasyonu"""
        if not password:
            return False, "Şifre gereklidir"
        
        if len(password) < min_length:
            return False, f"Şifre en az {min_length} karakter olmalıdır"
        
        return True, None
    
    @staticmethod
    def validate_length(value: str, field_name: str, min_length: Optional[int] = None,
                       max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Uzunluk validasyonu"""
        if value is None:
            value = ""
        
        value_str = str(value)
        if min_length is not None and len(value_str) < min_length:
            return False, f"{field_name} en az {min_length} karakter olmalıdır"
        if max_length is not None and len(value_str) > max_length:
            return False, f"{field_name} en fazla {max_length} karakter olmalıdır"
        return True, None

