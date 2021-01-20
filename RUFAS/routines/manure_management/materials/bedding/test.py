from base_bedding import *
from organic_bedding import *
from sand_bedding import *

"""
Bedding is tested by testing OrganicBedding and SandBedding
"""
def testBeddings():
    """
    Tests the functionality of the Bedding class in base_bedding.py
    """
    orgbed1 = OrganicBedding(mass=100)
    orgbed2 = OrganicBedding(10)
    orgbed3 = OrganicBedding(1,100) #Overides default density

    sndbed1 = SandBedding(mass=100)
    sndbed2 = SandBedding(10)
    sndbed3 = SandBedding(10,100)

    #Test Initializers
    print("Testing initializers...")
    assert orgbed1.getMass() == 100, "Mass not set or got properly with keyword"
    assert orgbed1.getVolume() == 0.4, "Volume or Density not set properly"
    assert orgbed2.getMass() == 10, "Mass not set or got properly without keyword"
    assert orgbed3.getMass() == 1, "Mass not set or got properly with density without keyword"
    assert orgbed3.getVolume() == 0.01, "Volume or Density not set properly"
    print("Initializer testing complete")

    #Test setters
    print("Testing setters...")
    orgbed3.setMass(10)
    assert orgbed3.getMass() == 10, "setMass() may be incorrect"
    assert orgbed3.getVolume() == 0.1, "_setVolume() or setMass() may be incorrect"
    print("Setters are working properly")

    #Test aggregateBedding()
    print("Testing aggregateBedding...")
    orgbed1.aggregateBedding(orgbed2)
    sndbed1.aggregateBedding(sndbed2)
    try:
        orgbed3.aggregateBedding(sndbed3)
    except AssertionError:
        pass
    except:
        raise Exception("Something went wrong")


    assert orgbed1.getMass() == 110
    assert orgbed1.getVolume() == 0.44
    assert sndbed1.getMass() == 110
    assert sndbed1.getVolume() == 11/150

    sndbed2.aggregateBedding(orgbed3)
    assert sndbed2.getMass() == 20
    assert sndbed2.getVolume() == 8/75
    assert sndbed2._density == 187.5

    print("aggregateBedding works.")


    print("Testing complete!")

if __name__ == '__main__':
    testBeddings()