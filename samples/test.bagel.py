import qm3.mol
import qm3.problem
import qm3.engines.bagel
import qm3.maths.matrix

try:
    import cStringIO as io
except:
    import io


class my_eng(qm3.problem.template):

    def __init__(self):
        self.mol = qm3.mol.molecule()
        self.mol.xyz_read("xyz")
        self.mol.chrg = [-0.834, 0.417, 0.417, -0.834, 0.417, 0.417]
        self.mol.anum = [8, 1, 1, 8, 1, 1]
        f = io.StringIO("""
{ "bagel": [
    qm3_guess
    {
    "title": "molecule",
    "basis": "./def2-svp.json",
    "df_basis": "./def2-fit.json",
    "angstrom": true,
    "geometry": qm3_atoms },
    { "title": "force", "export": true, "method": [ 
        { "title": "hf", "charge": "0", "nopen": "0", "thresh": "1.e-8", "maxiter": "500" } ] },
    { "title" : "save_ref", "file" : "bagel" }
] }
""")
        f.seek(0)
        self.eng = qm3.engines.bagel.bagel(self.mol, f, [0, 1, 2], [3, 4, 5])
        self.eng.exe = "/bin/bash ./bagel.run"

        self.size = 3 * self.mol.natm
        self.coor = self.mol.coor
        self.func = 0.0
        self.grad = []

    def get_func(self):
        self.mol.func = 0.0
        self.eng.get_func(self.mol)
        self.func = self.mol.func

    def get_grad(self):
        self.mol.func = 0.0
        self.mol.grad = [0.0 for i in range(self.size)]
        self.eng.get_grad(self.mol)
        self.func = self.mol.func
        self.grad = self.mol.grad


f = open("xyz", "wt")
f.write("""6

O       0.12109      0.06944     -0.22458
H      -0.52694      0.16499     -0.94583
H       0.70159     -0.63565     -0.54677
O      -0.45114      1.12675      2.21102
H      -0.29157      0.59483      1.39876
H       0.05804      1.92714      2.01036
""")
f.close()

f = open("bagel.run", "wt")
f.write("""
export BAGEL_NUM_THREADS=2
./bin/BAGEL bagel.json > bagel.log
""")
f.close()

f = open("def2-svp.json", "wt")
f.write("""
{
  "H" : [
    {
      "angular" : "s",
      "prim" : [13.0107010, 1.9622572, 0.44453796],
      "cont" : [[0.19682158E-01, 0.13796524, 0.47831935]]
    }, {
      "angular" : "s",
      "prim" : [0.12194962],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.8000000],
      "cont" : [[1.0000000]]
    }
  ],
  "O" : [
    {
      "angular" : "s",
      "prim" : [2266.1767785, 340.87010191, 77.363135167, 21.479644940, 6.6589433124],
      "cont" : [[-0.53431809926E-02, -0.39890039230E-01, -0.17853911985, -0.46427684959, -0.44309745172]]
    }, {
      "angular" : "s",
      "prim" : [0.80975975668],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [0.25530772234],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [17.721504317, 3.8635505440, 1.0480920883],
      "cont" : [[0.43394573193E-01, 0.23094120765, 0.51375311064]]
    }, {
      "angular" : "p",
      "prim" : [0.27641544411],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [1.2000000],
      "cont" : [[1.0000000]]
    }
  ]
}
""")
f.close()

f = open("def2-fit.json", "wt")
f.write("""
{
  "H" : [
    {
      "angular" : "s",
      "prim" : [22.0683430000, 4.3905712000, 1.0540787000],
      "cont" : [[0.0530339860, 0.3946522022, 0.9172987712]]
    }, {
      "angular" : "s",
      "prim" : [0.2717874000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [1.8529979000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.3881034000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [2.5579933000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [0.3292649000],
      "cont" : [[1.0000000]]
    }
  ],
  "O" : [
    {
      "angular" : "s",
      "prim" : [625.28298110, 253.93274180, 109.04929550, 49.423005600, 23.580521100],
      "cont" : [[0.18479249890, 0.19224605780, 0.59372043000, 0.60593463970, 0.45741933600]]
    }, {
      "angular" : "s",
      "prim" : [11.807759100],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [6.1827814000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [3.3709061000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [1.9042805000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [1.1085447000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [0.66098860000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [0.40108140000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [0.24597690000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "s",
      "prim" : [0.15139390000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [77.687483800, 22.415388400, 9.8906463000],
      "cont" : [[0.39010104350, 0.83793482660, 0.38168888150]]
    }, {
      "angular" : "p",
      "prim" : [5.4848863000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [2.9732983000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [1.4735260000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.73603410000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.36974140000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.18637210000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "p",
      "prim" : [0.94990600000E-01],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [37.707107400, 14.775254300, 5.8470900000],
      "cont" : [[0.77860015600E-01, 0.31355206270, 0.94637356360]]
    }, {
      "angular" : "d",
      "prim" : [2.3304365000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [0.93282670000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "d",
      "prim" : [0.37392850000],
      "cont" : [[1.0000000]]
    }, {
      "angular" : "f",
      "prim" : [3.0293422000],
      "cont" : [[0.76154791140]]
    }, {
      "angular" : "f",
      "prim" : [0.92484900000],
      "cont" : [[0.64810861640]]
    }, {
      "angular" : "g",
      "prim" : [1.6934809000],
      "cont" : [[1.0000000]]
    }
  ]
}
""")
f.close()

obj = my_eng()
obj.get_grad()
print(obj.func)
qm3.maths.matrix.mprint(obj.grad, obj.mol.natm, 3)
