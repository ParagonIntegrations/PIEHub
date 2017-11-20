import sqlite3

conn = sqlite3.connect('PIEHub.db')

c = conn.cursor()

# Create table
c.execute('''CREATE TABLE PIEHub(DateTime, ID, Frequency, PLL, V1, I1, PowerFactor1, PImport1, PExport1, UnitsUsed1, Units1)''')

# Save (commit) the changes
conn.commit()

# We can also close the connection if we are done with it.
# Just be sure any changes have been committed or they will be lost.
conn.close()