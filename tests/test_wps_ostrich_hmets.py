import datetime as dt
from urllib.request import urlretrieve

import numpy as np
from pywps import Service
from pywps.tests import assert_response_success
from ravenpy.utilities.testdata import get_local_testdata

from raven.processes import OstrichHMETSProcess

from .common import CFG_FILE, client_for, get_output


class TestOstrichHMETSProcess:
    def test_simple(self):
        client = client_for(
            Service(processes=[OstrichHMETSProcess()], cfgfiles=CFG_FILE)
        )

        lowerBounds = "0.3, 0.01, 0.5, 0.15, 0.0, 0.0, -2.0, 0.01, 0.0, 0.01, 0.005, -5.0, \
                      0.0, 0.0, 0.0, 0.0, 0.00001, 0.0, 0.00001, 0.0, 0.0"
        upperBounds = "20.0, 5.0, 13.0, 1.5, 20.0, 20.0, 3.0, 0.2, 0.1, 0.3, 0.1, 2.0, 5.0, \
                      1.0, 3.0, 1.0, 0.02, 0.1, 0.01, 0.5, 2.0"

        datainputs = (
            "ts=files@xlink:href=file://{ts};"
            "algorithm={algorithm};"
            "max_iterations={max_iterations};"
            "lowerBounds={lowerBounds};"
            "upperBounds={upperBounds};"
            "start_date={start_date};"
            "duration={duration};"
            "name={name};"
            "run_name={run_name};"
            "area={area};"
            "latitude={latitude};"
            "longitude={longitude};"
            "elevation={elevation};"
            "random_numbers=files@xlink:href=file://{random_numbers};"
            "random_seed=0".format(
                ts=get_local_testdata(
                    "raven-gr4j-cemaneige/Salmon-River-Near-Prince-George_meteo_daily.nc",
                ),
                algorithm="DDS",
                max_iterations=10,
                lowerBounds=lowerBounds,
                upperBounds=upperBounds,
                start_date=dt.datetime(1954, 1, 1),
                duration=208,
                name="Salmon",
                run_name="test",
                area="4250.6",
                elevation="843.0",
                latitude=54.4848,
                longitude=-123.3659,
                random_numbers=get_local_testdata(
                    "ostrich-gr4j-cemaneige/OstRandomNumbers.txt"
                ),
            )
        )

        resp = client.get(
            service="WPS",
            request="Execute",
            version="1.0.0",
            identifier="ostrich-hmets",
            datainputs=datainputs,
        )

        assert_response_success(resp)

        out = get_output(resp.xml)
        assert "diagnostics" in out
        tmp_file, _ = urlretrieve(out["diagnostics"])
        tmp_content = open(tmp_file).readlines()

        # checking correctness of NSE (full period 1954-2010 with budget 50 would be NSE=0.5779910)
        assert "DIAG_NASH_SUTCLIFFE" in tmp_content[0]
        idx_diag = tmp_content[0].split(",").index("DIAG_NASH_SUTCLIFFE")
        diag = float(tmp_content[1].split(",")[idx_diag])

        np.testing.assert_almost_equal(
            diag, -1.43474, 4, err_msg="NSE is not matching expected value"
        )

        # checking correctness of RMSE (full period 1954-2010 with budget 50 would be RMSE=????)
        assert "DIAG_RMSE" in tmp_content[0]
        idx_diag = tmp_content[0].split(",").index("DIAG_RMSE")
        diag = float(tmp_content[1].split(",")[idx_diag])

        np.testing.assert_almost_equal(
            diag, 80.8459, 4, err_msg="RMSE is not matching expected value"
        )

    def test_no_test(self):
        client = client_for(
            Service(processes=[OstrichHMETSProcess()], cfgfiles=CFG_FILE)
        )

        params = "9.5019, 0.2774, 6.3942, 0.6884, 1.2875, 5.4134, 2.3641, 0.0973, 0.0464, 0.1998,  \
                        0.0222, -1.0919, 2.6851, 0.3740, 1.0000, 0.4739, 0.0114, 0.0243, 0.0069, 0.3107211, 0.9161947"
        lowerBounds = "0.3, 0.01, 0.5, 0.15, 0.0, 0.0, -2.0, 0.01, 0.0, 0.01, 0.005, -5.0, \
                             0.0, 0.0, 0.0, 0.0, 0.00001, 0.0, 0.00001, 0.0, 0.0"
        upperBounds = "20.0, 5.0, 13.0, 1.5, 20.0, 20.0, 3.0, 0.2, 0.1, 0.3, 0.1, 2.0, 5.0, \
                             1.0, 3.0, 1.0, 0.02, 0.1, 0.01, 0.5, 2.0"

        datainputs = (
            "ts=files@xlink:href=file://{ts};"
            "algorithm={algorithm};"
            "max_iterations={max_iterations};"
            "params={params};"
            "lowerBounds={lowerBounds};"
            "upperBounds={upperBounds};"
            "start_date={start_date};"
            "duration={duration};"
            "name={name};"
            "run_name={run_name};"
            "area={area};"
            "latitude={latitude};"
            "longitude={longitude};"
            "elevation={elevation};".format(
                ts=get_local_testdata(
                    "raven-gr4j-cemaneige/Salmon-River-Near-Prince-George_meteo_daily.nc",
                ),
                algorithm="DDS",
                max_iterations=10,
                params=params,
                lowerBounds=lowerBounds,
                upperBounds=upperBounds,
                start_date=dt.datetime(1954, 1, 1),
                duration=208,
                name="Salmon",
                run_name="test",
                area="4250.6",
                elevation="843.0",
                latitude=54.4848,
                longitude=-123.3659,
            )
        )

        resp = client.get(
            service="WPS",
            request="Execute",
            version="1.0.0",
            identifier="ostrich-hmets",
            datainputs=datainputs,
        )

        assert_response_success(resp)
