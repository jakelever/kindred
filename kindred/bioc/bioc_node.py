__all__ = ['BioCNode']

class BioCNode:

    def __init__(self, node=None, refid=None, role=None):
        
        self.refid = ''
        self.role = ''

        # Use arg ``node'' if set
        if node is not None:
            self.refid = node.refid
            self.role = node.role
        # Use resting optional args only if both set
        elif (refid is not None) and (role is not None):
            self.refid = refid
            self.role = role

    def __str__(self):
         s = 'refid: ' + self.refid + '\n'
         s += 'role: ' + self.role + '\n'

         return s
