Tutorials
=========

For more information on Python itself, see `their web site <https://python.org/>`_.


An Introduction
---------------

The rpl-pack package contains modules for separate progam interfaces that need
to be logged into.

Here is a short example of how we can calculate properties of brine, and use matplotlib 
to visualize some data.

.. code-block:: python

    import numpy as np
    
    from rpl_pack.flag import Brine

    # Instantiate application interface
    brine = Brine('username', 'password')

    # Make computation request to RPL server
    temperature = np.linspace(1., 100., 100) # deg C
    pressure = 20    # MPa
    salinity = 50000 # ppm
    NaCL = 100       # weight %
    KCl = 0          # weight %
    CaCl2 = 0        # weight %
    Vb = brine.velocity_brine(temperature, pressure, salinity, NaCL, KCl, CaCl2)

    # Plot velocity of brine against temperature
    fig = plt.figure()
    plt.plot(temperature, Vb)
    plt.show()
