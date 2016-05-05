__author__ = 'cphillips'

import os

import dmv


def get_max_vector_length(cdf):
    dims = cdf.dimensions.copy()
    del dims['time']
    return len(max(dims.values(), key=len))


def get_records(cdf):
    for record in xrange(len(cdf.dimensions['time'])):
        scalars = {}
        vectors = {}
        for variable in cdf.variables:
            if variable.endswith('_ind'):
                continue
            if len(cdf.variables[variable].dimensions) == 1:
                scalars[str(variable)] = cdf.variables[variable][record]
            else:
                vectors[str(variable)] = cdf.variables[variable][record, :]
        yield scalars, vectors, record


def get_vector_names(cdf):
    vectors = set([])
    for variable in cdf.variables:
        if variable.endswith('_ind'):
            continue
        if len(cdf.variables[variable].dimensions) > 1:
            vectors.add(variable)
    return vectors


def add_subheaders(fp, file_type):
    if file_type == 'SUM':
        fp.addHousekeepingSubheader()
        # AERICALV
        fp.addSubheader(dmv.ints(1, 97122201))
        # FFOV
        fp.addSubheader(dmv.ints(1, 94030401))
        # ZFLI
        fp.addSubheader(dmv.ints(1, 94030402))

        # SCNDIRAV
        fp.addSubheader(dmv.ints(1, 94030301))
        # NLAPP
        fp.addSubheader(dmv.ints(1, 94051001))
        # AERISUM
        fp.addSubheader(dmv.ints(1, 97050704))
    if file_type == 'CXS':
        fp.addHousekeepingSubheader()
        fp.addSubheader(dmv.ints(1, 97050702))
        pass


def create_file(filepath, max_vector_length, vector_table, file_type):
    if os.path.isfile(filepath):
        os.unlink(filepath)
    fp = dmv.dmv()
    add_subheaders(fp, file_type)

    fp.setApplication('')
    name2vid = {}
    for vid, vec_sname, vec_lname, vec_label, vec_units, vec_precision in vector_table:
        fp.newVector(vid, 1.0, float(max_vector_length), max_vector_length)
        fp.setVectorShortname(vec_sname)
        fp.setVectorLongname(vec_lname)
        fp.setVectorLabel(vec_label)
        fp.setVectorUnits(vec_units)
        try:
            fp.setVectorPrecision(int(0), int(vec_precision))
        except ValueError:
            fp.setVectorPrecision(0, -3)
        fp.commitNewVector()
        name2vid[vec_sname] = vid
    rc = fp.createFile(filepath)
    assert (rc == 0)
    return fp, name2vid


def write_record(fp, scalars, vectors, name2vid, record):
    scalar_tmp = [(fp.findMetaID(key), val) for (key, val) in scalars.items()]
    scalar_ids = dmv.ints([x[0] for x in scalar_tmp])
    scalar_vals = dmv.floats([x[1] for x in scalar_tmp])
    rc = fp.newRecord(record)
    assert rc == 0
    for vector, values in vectors.items():
        if vector in name2vid:
            rc = fp.addVector(name2vid[vector], dmv.floats(values))
        assert rc == 0
    rc = fp.addMeta(scalar_ids, scalar_vals)
    assert rc == 0
    rc = fp.commitNewRecord()
    assert rc == 0


def get_vector_table(dmv_file):
    d = dmv.dmv(dmv_file)
    types = [dmv.dmv.SHORTNAME, dmv.dmv.LONGNAME, dmv.dmv.LABEL, dmv.dmv.UNITS, dmv.dmv.PRECISION]
    for vector_id in d.vectorIDs():
        yield (vector_id,) + tuple(d.queryVectorDescString(vector_id, t) for t in types)


def convert_cdf_to_dmv(cdf, dmv_file, vector_table):
    if dmv_file.lower().endswith('.cxs'):
        file_type = 'CXS'
    elif dmv_file.lower().endswith('.sum'):
        file_type = 'SUM'
    else:
        raise NotImplemented

    max_vector_length = get_max_vector_length(cdf)
    fp, name2vid = create_file(dmv_file, max_vector_length, vector_table, file_type)
    for scalars, vectors, record in get_records(cdf):
        write_record(fp, scalars, vectors, name2vid, record + 1)
