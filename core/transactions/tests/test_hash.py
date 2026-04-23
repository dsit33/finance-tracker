from datetime import date                                                                                                                                                      
from decimal import Decimal                       
                                    
from transactions.hashing import compute_import_hash

def test_same_inputs_produce_same_hash():
    args = ("ext-1", date(2026, 4, 22), Decimal("12.99"), "NETFLIX")                                                                                                  
    assert compute_import_hash(*args) == compute_import_hash(*args)
                                                                                                                                                                                

def test_different_inputs_produce_different_hash():                                                                                                                            
    base = ("ext-1", date(2026, 4, 22), Decimal("12.99"), "NETFLIX")
    changed = (*base[:-1], "netflix")                                                                                                                                           
    assert compute_import_hash(*base) != compute_import_hash(*changed)