import sqlite3


class Cache():
    def __init__(self, db):
        self._conn = sqlite3.connect(db)
        self._cur = self._conn.cursor()

        self._cur.executescript('''CREATE TABLE IF NOT EXISTS Updates (
                                   archive TEXT UNIQUE,
                                   last_update TEXT);

                                   CREATE TABLE IF NOT EXISTS Packages (
                                   id INTEGER PRIMARY KEY,
                                   pkg_name TEXT UNIQUE,
                                   homepage TEXT,
                                   in_debian INTEGER,
                                   is_builtin INTEGER);

                                   CREATE TABLE IF NOT EXISTS Spacemacs (
                                   id INTEGER UNIQUE,
                                   layer TEXT);

                                   CREATE TABLE IF NOT EXISTS DoomEmacs (
                                   id INTEGER UNIQUE,
                                   layer TEXT)''')

        self._cur.execute('''SELECT name FROM sqlite_master
                             WHERE type="table" AND name!="Updates"''')
        self._tables = [table for (table,) in self._cur.fetchall()]

    def last_update(self, archive):
        self._cur.execute('''SELECT last_update FROM Updates
                             WHERE archive=?''', (archive,))
        return self._cur.fetchone()[0]

    def update_last_update(self, archive, last_update):
        self._cur.execute('''INSERT OR REPLACE INTO Updates
                             VALUES (?,?)''', (archive, last_update))
        self._conn.commit()

    def _add_layers(self, pkg_dict):
        layers = dict()
        for suit in ['Spacemacs', 'DoomEmacs']:
            command = f'SELECT layer FROM {suit} WHERE id=?'
            self._cur.execute(command, (pkg_dict['id'],))
            layer = self._cur.fetchone()
            if layer:
                layers[suit.lower()] = layer[0]
            else:
                layers[suit.lower()] = ''
        return layers

    def get_packages(self):
        self._conn.row_factory = sqlite3.Row
        _c_row = self._conn.cursor()
        _c_row.execute('SELECT * FROM Packages')
        pkgs = []
        for pkg in _c_row.fetchall():
            pkg = dict(pkg)
            pkg.update(self._add_layers(pkg))
            pkg.pop('id', None)
            pkgs.append(pkg)
        return pkgs

    def _update_package(self, pkg):
        self._cur.execute('''SELECT id FROM Packages
                             WHERE pkg_name=?''', (pkg['pkg_name'],))
        try:
            id = self._cur.fetchone()[0]
            for suit in ['Spacemacs', 'DoomEmacs']:
                command = f'''DELETE FROM {suit} WHERE id=?'''
                self._cur.execute(command, (id,))
        except TypeError:
            pass    # no such package, nothing to delete from suits
        self._cur.execute('''INSERT OR REPLACE INTO Packages
                             (pkg_name, homepage, in_debian, is_builtin)
                             VALUES (?, ?, ?, ?)''', (pkg['pkg_name'],
                                                      pkg['homepage'],
                                                      pkg['in_debian'],
                                                      pkg['is_builtin']))
        self._cur.execute('''SELECT id FROM Packages
                             WHERE pkg_name=?''', (pkg['pkg_name'],))
        id = self._cur.fetchone()[0]
        for suit in ['Spacemacs', 'DoomEmacs']:
            if suit.lower() in pkg:
                command = f'''INSERT OR REPLACE INTO {suit} (id, layer)
                              VALUES (?, ?)'''
                self._cur.execute(command, (id, pkg[suit.lower()]))
        self._conn.commit()

    def update_packages(self, pkgs):
        for pkg in pkgs:
            self._update_package(pkg)

    def drop_package(self, pkg):
        self._cur.execute('''SELECT id FROM Packages
                             WHERE pkg_name=?''', (pkg, ))
        try:
            id = self._cur.fetchone()[0]
            for table in self._tables:
                delete_command = f'DELETE FROM {table} WHERE id=?'
                self._cur.execute(delete_command, (id,))
            self._conn.commit()
        except TypeError:
            print(f'Package {pkg} not found in cache.')

    def is_builtin(self, pkg):
        self._cur.execute('''SELECT is_builtin FROM Packages
                             WHERE pkg_name=?''', (pkg,))
        try:
            if self._cur.fetchone()[0]:
                return True
            else:
                return False
        except TypeError:
            print(f'Package {pkg} not found in cache.')

    def get_builtins(self):
        builtins = []
        for pkg in self.get_packages():
            if pkg['is_builtin']:
                builtins.append(pkg['pkg_name'])
        return builtins

    def clean_db(self):
        pkgs = self.get_packages()
        for pkg in pkgs:
            if not pkg['spacemacs'] and not pkg['doomemacs']:
                self.drop_package(pkg['pkg_name'])

    def drop_suites(self):
        for suit in ['Spacemacs', 'DoomEmacs']:
            command = f'DELETE FROM {suit}'
            self._cur.execute(command)
