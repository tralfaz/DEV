import numpy

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

MASS_RANGE = (10.0, 50.0)
POSITION_RANGE = (-50.0, 50.0)
VELOCITY_RANGE = (-5.0, 5.0)

if __name__ == '__main__':
    nbodies = 5
 
    masses = numpy.random.rand(nbodies)
    masses *= (MASS_RANGE[1] - MASS_RANGE[0])
    masses += MASS_RANGE[0]
    print(f"MASSES: {masses}")

    positions = numpy.random.rand(nbodies, 3)
    positions *= (POSITION_RANGE[1] - POSITION_RANGE[0])
    positions += POSITION_RANGE[0]
    print(f"POSITIONS: {positions}")

    velocities = numpy.random.rand(nbodies, 3)
    velocities *= (VELOCITY_RANGE[1] - VELOCITY_RANGE[0])
    velocities += VELOCITY_RANGE[0]
    print(f"VELOCITIES: {velocities}")

    print(f"P0: {positions[0]} P1: {positions[1]} P0->P1: {positions[1]-positions[0]}")
    p0dists = numpy.delete(positions, 0, axis=0)
    p0dists -= positions[0]
    print(f"P0-P[1:]: {p0dists}")
