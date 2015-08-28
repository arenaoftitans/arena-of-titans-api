import coverage
import logging


cov = coverage.coverage(config_file=False)
cov.start()


from aot.main import main


logging.basicConfig(level=logging.DEBUG)
main(debug=True)

cov.report(omit=['/usr/lib/*'])
cov.stop()
cov.save()
cov.html_report(directory='htmlcovapi')
