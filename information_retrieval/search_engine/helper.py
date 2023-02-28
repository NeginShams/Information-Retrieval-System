class IdMap:
    """Helper class to store a mapping from strings to ids."""

    def __init__(self):
        self.str_to_id = {}
        self.id_to_str = {}
        self.doc_to_id = {}

    def __len__(self):
        """Return number of terms stored in the IdMap"""
        return len(self.id_to_str)

    def _get_str(self, i):
        """Returns the string corresponding to a given id (`i`)."""
        
        self.id_to_str = {y:x for x,y in self.str_to_id.items()}
        return self.id_to_str.get(i)
        
        
    def _get_doc_id(self, s):
        if s not in self.str_to_id:
            value = len(self.doc_to_id) 
            self.doc_to_id[s] = value
            return value
        else:
            return self.doc_to_id.get(s)
        
    def _get_doc_str(self, i):
        self.doc_id_to_str = {y:x for x,y in self.doc_to_id.items()}
        return self.doc_id_to_str.get(i)
        

    def _get_id(self, s):
        """Returns the id corresponding to a string (`s`).
        If `s` is not in the IdMap yet, then assigns a new id and returns the new id.
        """
        
        if s not in self.str_to_id:
            value = len(self.str_to_id) 
            self.str_to_id[s] = value
            return value
        else:
            return self.str_to_id.get(s)

        

    def __getitem__(self, key):
        """If `key` is a integer, use _get_str;
           If `key` is a string, use _get_id;"""
        if type(key) is int:
            return self._get_str(key)
        elif type(key) is str:
            return self._get_id(key)
        else:
            raise TypeError