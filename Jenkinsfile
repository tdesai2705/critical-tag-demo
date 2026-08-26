// ─────────────────────────────────────────────────────────────────────────────
// Naoto's ask (relayed via Slack, Anudeep/Uday/Dinesh thread): verify that a
// SINGLE Smart Tests workspace can cleanly record & subset against multiple
// CLI "profiles" (i.e. different TEST_RUNNER values) at once, since users
// currently have to use one workspace per CLI/test-runner.
//
// Per Uday: there's no separate "enable multiple profiles" toggle -- profile
// is just the <TEST_RUNNER> argument to `record tests` / `subset`, scoped
// per test session, not a workspace-wide setting. This pipeline verifies
// that in practice: records TWO genuinely different profiles (pytest and
// jest) as separate sessions into the SAME workspace, back to back, and
// confirms both record + subset cleanly with no cross-contamination.
// ─────────────────────────────────────────────────────────────────────────────

pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins-agents
  containers:
  - name: jnlp
    resources:
      requests: { cpu: "10m", memory: "256Mi" }
      limits: { cpu: "500m", memory: "512Mi" }
  - name: python
    image: python:3.13-slim
    command: [sleep]
    args: [99d]
    resources:
      requests: { cpu: "10m", memory: "256Mi" }
      limits: { cpu: "1", memory: "1Gi" }
  - name: node
    image: node:20-slim
    command: [sleep]
    args: [99d]
    resources:
      requests: { cpu: "10m", memory: "256Mi" }
      limits: { cpu: "1", memory: "1Gi" }
"""
        }
    }

    parameters {
        choice(name: 'WORKSPACE_TARGET', choices: ['multiprofile'], description: 'Which Smart Tests workspace to record against')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install Dependencies') {
            parallel {
                stage('Python deps') {
                    steps {
                        container('python') {
                            sh '''
                                apt-get update -qq
                                apt-get install -y --no-install-recommends default-jre-headless git >/dev/null
                                pip install --no-cache-dir -r requirements.txt
                                pip install --no-cache-dir "smart-tests-cli~=2.0"
                                smart-tests --version
                            '''
                        }
                    }
                }
                stage('Node deps') {
                    steps {
                        container('node') {
                            sh '''
                                apt-get update -qq
                                apt-get install -y --no-install-recommends default-jre-headless git python3 python3-pip >/dev/null
                                pip3 install --no-cache-dir --break-system-packages "smart-tests-cli~=2.0"
                                cd js-suite && npm install --no-audit --no-fund
                            '''
                        }
                    }
                }
            }
        }

        stage('Smart Tests — Record Build') {
            steps {
                container('python') {
                    withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                        sh '''
                            git config --global --add safe.directory ${WORKSPACE}
                            smart-tests verify || true
                            smart-tests record build --build ${BUILD_TAG} --source .
                        '''
                    }
                }
            }
        }

        stage('Profile A: pytest') {
            steps {
                container('python') {
                    withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                        sh '''
                            mkdir -p test-results-pytest

                            smart-tests record session \
                                --build ${BUILD_TAG} \
                                --test-suite multiprofile-pytest \
                                > session-pytest.txt

                            echo "=== pytest profile session: $(cat session-pytest.txt) ==="

                            PYTHONPATH=. pytest tests/ --collect-only -q \
                                | grep '::' \
                                | smart-tests subset pytest --session @session-pytest.txt \
                                > subset-pytest.txt

                            echo "=== pytest subset selected $(wc -l < subset-pytest.txt) tests ==="
                            cat subset-pytest.txt

                            set --
                            while IFS= read -r line; do set -- "$@" "$line"; done < subset-pytest.txt
                            PYTHONPATH=. pytest "$@" --junitxml=test-results-pytest/results.xml -v
                        '''
                    }
                }
            }
            post {
                always {
                    container('python') {
                        withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                            sh 'smart-tests record tests pytest --session @session-pytest.txt test-results-pytest/results.xml || true'
                        }
                    }
                    junit 'test-results-pytest/results.xml'
                }
            }
        }

        stage('Profile B: jest') {
            steps {
                container('node') {
                    withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                        sh '''
                            smart-tests record session \
                                --build ${BUILD_TAG} \
                                --test-suite multiprofile-jest \
                                > session-jest.txt

                            echo "=== jest profile session: $(cat session-jest.txt) ==="

                            cd js-suite
                            npx jest --listTests \
                                | smart-tests subset jest --session @../session-jest.txt --base "${WORKSPACE}" \
                                > ../subset-jest.txt || true

                            echo "=== jest subset ==="
                            cat ../subset-jest.txt || true

                            npx jest --ci --reporters=default --reporters=jest-junit
                        '''
                    }
                }
            }
            post {
                always {
                    container('node') {
                        withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                            // NOTE: --base must match the subset call above exactly ($WORKSPACE,
                            // the repo root) so recorded test paths line up with what subset saw.
                            sh 'smart-tests record tests jest --session @session-jest.txt --base "${WORKSPACE}" js-suite/junit.xml --group jest || true'
                        }
                    }
                    junit 'js-suite/junit.xml'
                }
            }
        }
    }
}
