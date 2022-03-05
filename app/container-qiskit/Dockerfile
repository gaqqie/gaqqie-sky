FROM public.ecr.aws/lambda/python:3.8

COPY container-qiskit/requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt
RUN mkdir ${LAMBDA_TASK_ROOT}/gaqqie_sky

COPY gaqqie_sky ${LAMBDA_TASK_ROOT}/gaqqie_sky

CMD [ "gaqqie_sky.provider.ibm_provider.submit_job" ]
