'''
Created on 20/10/2017

@author: ernesto
'''
import logging
import sys
from operator import add, sub
nivel_log = logging.ERROR
#nivel_log = logging.DEBUG
logger_cagada = None

from bisect import bisect_left, bisect_right

class SortedCollection(object):
    '''Sequence sorted by a key function.

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attibute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    '''

    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key

    def _getkey(self):
        return self._key

    def _setkey(self, key):
        if key is not self._key:
            self.__init__(self._items, key=key)

    def _delkey(self):
        self._setkey(None)

    key = property(_getkey, _setkey, _delkey, 'key function')

    def clear(self):
        self.__init__([], self._key)

    def copy(self):
        return self.__class__(self, self._key)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        'Return number of occurrences of item'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def insert_right(self, item):
        'Insert a new item.  If equal keys are found, add to the right'
        k = self._key(item)
        i = bisect_right(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: %r' % (k,))

    def find_le(self, k):
        'Return last item with a key <= k.  Raise ValueError if not found.'
        i = bisect_right(self._keys, k)
        if i:
            return self._items[i - 1]
        raise ValueError('No item found with key at or below: %r' % (k,))

    def find_lt(self, k):
        'Return last item with a key < k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i:
            return self._items[i - 1]
        raise ValueError('No item found with key below: %r' % (k,))

    def find_ge(self, k):
        'Return first item with a key >= equal to k.  Raise ValueError if not found'
        i = bisect_left(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key at or above: %r' % (k,))

    def find_gt(self, k):
        'Return first item with a key > k.  Raise ValueError if not found'
        i = bisect_right(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key above: %r' % (k,))


def cacadena_es_subsequencia(cadenota, cadenita, posiciones_cadenota):
    idx_act = -1
    si = True
    posiciones_subseq = SortedCollection()
    for carajo in cadenita:
        try:
            idx_act = posiciones_cadenota[carajo].find_gt(idx_act)
        except ValueError as e:
            si = False
            break 
        posiciones_subseq.insert(idx_act)
    return posiciones_subseq if si else None

def cacadena_remover_posicion(cadenota, posiciones_cadena, posicion):
    letra = cadenota[posicion]
    posiciones_cadena[letra].remove(posicion)
    return letra

def cacadena_genera_posiciones_cadena(cadenota, posiciones_cadena):
    for posicion, letra in enumerate(cadenota):
        posiciones_cadena.setdefault(letra, SortedCollection()).insert(posicion)
    
#    logger_cagada.debug("las posiciones de {} son {}".format(letra, posiciones_cadena))

def cadena_remover_posiciones(cadenota, posiciones_cadena, indices_culeros, respaldo):
    logger_cagada.debug("los idxs q c kitan {}".format(indices_culeros))
    for idx_a_borrar in indices_culeros:
        letra = cacadena_remover_posicion(cadenota, posiciones_cadena, idx_a_borrar)
        respaldo.append((idx_a_borrar, letra))
        
def cadena_restaurar_posiciones(cadenota, posiciones_cadena, respaldo):
    for idx_borrado, letra in respaldo:
        posiciones_cadena[letra].insert(idx_borrado)

def cadena_poner_posiciones(cadenota, posiciones_cadena, indices_culeros, respaldo):
    logger_cagada.debug("los idxs q c ponen {}".format(indices_culeros))
    for idx_a_poner in indices_culeros:
        letra = cadenota[idx_a_poner]
        respaldo.append((idx_a_poner, letra))
    cadena_restaurar_posiciones(cadenota, posiciones_cadena, respaldo)

def cacadena_core(cadenota, cadenita, indices_culeros):
    posiciones_cadena = {}
    idx_borrados_cnt = 0
    cacadena_genera_posiciones_cadena(cadenota, posiciones_cadena)
    
    operacion = add
    pot_2 = 1
    delta = len(cadenota)
    while pot_2 < delta:
        pot_2 <<= 1
    delta = pot_2
    tam_brinco = 0
    ultimo_bueno = 0
    cadenota_tam = len(cadenota)
    while True:
        respaldo = []
        posiciones_subseq = None
        idx_ini = 0
        idx_fin = 0
        operacion_en_posiciones_letra = None
        tam_brinco = operacion(tam_brinco, delta)

        logger_cagada.debug("el brinco es {} l delta {}".format(tam_brinco, delta))
        if(operacion == add):
            idx_ini = tam_brinco - delta
            idx_fin = tam_brinco
            operacion_en_posiciones_letra = cadena_remover_posiciones
        else:
            idx_ini = tam_brinco 
            idx_fin = tam_brinco + delta
            operacion_en_posiciones_letra = cadena_poner_posiciones
        logger_cagada.debug("el idx ini {} idx fin {}".format(idx_ini, idx_fin))
        
        operacion_en_posiciones_letra(cadenota, posiciones_cadena, indices_culeros[idx_ini:idx_fin], respaldo)
        posiciones_subseq = cacadena_es_subsequencia(cadenota, cadenita, posiciones_cadena)
        if(posiciones_subseq):
            if(delta == len(cadenita) or delta == 1):
                break
            operacion = add
            ultimo_bueno = tam_brinco
        else:
            if(delta == 1):
                tam_brinco = 0
                break
            operacion = sub
        delta >>= 1
    
    return tam_brinco if tam_brinco else ultimo_bueno

def cacadena_main():
    lineas = list(sys.stdin)
    cadenota = lineas[0].strip()
    cadenita = lineas[1].strip()
    cacas = [int(x) - 1 for x in lineas[2].strip().split(" ")]
    
    mierda = cacadena_core(cadenota, cadenita, cacas)
    logger_cagada.debug("la mierda es {}".format(mierda))
    print("{}".format(mierda))

if __name__ == '__main__':
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(level=nivel_log, format=FORMAT)
    logger_cagada = logging.getLogger("asa")
    logger_cagada.setLevel(nivel_log)
    cacadena_main()
