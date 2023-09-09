import dbdreader

pattern="../data/amadeus-2014-*.[st]bd"

multi = dbdreader.MultiDBD(pattern=pattern)

#output = multi.get("c_wpt_lon")
output = multi.get("m_depth", "m_pitch", include_source=True)
output = multi.get("m_depth", include_source=False)

for parameter in multi.parameterNames["eng"] + multi.parameterNames["sci"]:
    output = multi.get(parameter, include_source=True)
    dbds = set(output[2])  # Unique source DBDs for this parameter
    for dbd in dbds:
        mask = output[2] == dbd
        content = [output[0][mask], output[1][mask]]  # Only data attributed to this DBD
        single = dbd.get(parameter)
        # Data should be identical
        assert all(content[0] == single[0])
        assert all(content[1] == single[1])

    # def test_include_source_files(self):
    #     print("Verify that all designated files are represented in sources.")
    #     files = glob.glob(self.pattern)
    #     multi = dbdreader.MultiDBD(pattern=self.pattern)

    #     output = multi.get(*(multi.parameterNames["eng"] + multi.parameterNames["sci"]), include_source=True)

    #     sources = {dbd.filename for parameter in output for dbd in parameter[2]}  # Unique source DBDs
    #     # All files should be represented
    #     assert all(file in sources for file in files)
    #     assert all(source in files for source in sources)
