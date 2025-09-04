#FROM docker-dev-local.repo.eap.aon.com/affinity/python-lambda:3.8
FROM docker-dev-local.repo.eap.aon.com/affinity/python-lambda:3.12.2

ARG DF_DATABASE_MODELS_DEPLOY_TOKEN_USERNAME="df_database_models"
ARG DF_DATABASE_MODELS_DEPLOY_TOKEN_PASSWORD=""
ARG ADF_PYUTILS_DEPLOY_TOKEN_USERNAME="adf_pyutils"
ARG ADF_PYUTILS_DEPLOY_TOKEN_PASSWORD=""

# Red Hat Enterprise Server 8 and Oracle Linux 8
RUN curl https://packages.microsoft.com/config/rhel/8/prod.repo > /etc/yum.repos.d/mssql-release.repo

#RUN yum install -y git && python3 -m pip install --upgrade pip

RUN ACCEPT_EULA=Y dnf install -y msodbcsql17

RUN pip install --upgrade pip

#COPY requirements.txt ./
#RUN python3 -m pip install --upgrade -r requirements.txt

RUN python3 -m pip install -v --no-cache-dir "df_database_models@git+https://$DF_DATABASE_MODELS_DEPLOY_TOKEN_USERNAME:$DF_DATABASE_MODELS_DEPLOY_TOKEN_PASSWORD@gitlab.com/aon/affinity/ods/df_database_models.git" 
RUN python3 -m pip install -v --no-cache-dir aon_df_commonloggingmodule --extra-index-url https://artifactory.aon.com/artifactory/api/pypi/dfclm-df-clm-pypi-dev-local/simple
RUN python3 -m pip install -v --no-cache-dir "adf_pyutils@git+https://$ADF_PYUTILS_DEPLOY_TOKEN_USERNAME:$ADF_PYUTILS_DEPLOY_TOKEN_PASSWORD@gitlab.com/aon/affinity/ods/ods_affinitydatafoundation_pyutils.git" 

COPY src/*.py ./
COPY src/*.json ./

CMD ["handler.handle"]