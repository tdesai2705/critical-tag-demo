// ─────────────────────────────────────────────────────────────────────────────
// Fresh, fast, purpose-built repo for testing Usha's (Amadeus) actual ask:
// Robot Framework can tag a test "critical" and prioritize/always-run it.
// TTS and Playwright have no such tag. Can Smart Tests achieve the same
// outcome via --prioritized-tests-mapping, correctly formatted per
// https://docs.cloudbees.com/docs/cloudbees-smart-tests/latest/send-data-to-smart-tests/subset/combine-with-rule-based-test-selection
// (mapping: repo -> real source directory -> list of test paths)?
//
// 3 features (pricing, shipping, inventory), each with 2 tests marked
// @pytest.mark.critical. Mapping maps each feature's real source directory
// to ONLY its critical tests (not all tests) -- that's the "tag" proxy.
//
// Small + fast on purpose (16 tests, ~3s total) so duration history builds
// in seconds, not hours, unlike the real todo-backend app.
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
"""
        }
    }

    parameters {
        choice(name: 'WORKSPACE_TARGET', choices: ['ptsv1', 'ptsv2'], description: 'Which clean Smart Tests workspace to record against')
        booleanParam(name: 'SMART_TESTS_OBSERVATION', defaultValue: false, description: 'Observation mode (ON to build duration history, OFF to test subsetting)')
        choice(name: 'SUBSET_MODE', choices: ['target', 'confidence'], description: 'Which optimization target to use when not in observation mode')
        string(name: 'SUBSET_VALUE', defaultValue: '20%', description: 'e.g. 20% for target, 70% for confidence')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install Dependencies') {
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

        stage('Generate mapping (repo -> real directory -> critical tests only)') {
            steps {
                container('python') {
                    sh '''
                        PYTHONPATH=. pytest tests/ --collect-only -q -m critical | grep "::" > critical-node-ids.txt || true
                        echo "Critical tests found:"
                        cat critical-node-ids.txt

                        python3 - <<'PYEOF'
import json

# test_pricing.py -> app/pricing, test_shipping.py -> app/shipping, etc.
by_dir = {}
with open("critical-node-ids.txt") as f:
    for line in f:
        node_id = line.strip()
        if not node_id:
            continue
        file_path, testcase = node_id.split("::")
        feature = file_path.split("/")[-1].replace("test_", "").replace(".py", "")
        directory = f"app/{feature}"
        module = file_path.replace("/", ".").rsplit(".py", 1)[0]
        entry = f"file={file_path}#class={module}#testcase={testcase}"
        by_dir.setdefault(directory, []).append(entry)

mapping = {"format": "prioritized-tests-v1", "mappings": {".": by_dir}}

with open("smart-tests-mapping.json", "w") as f:
    json.dump(mapping, f, indent=2)

print(json.dumps(mapping, indent=2))
PYEOF
                    '''
                }
            }
        }

        stage('Test') {
            steps {
                container('python') {
                    withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                        script {
                            def obsFlag = params.SMART_TESTS_OBSERVATION ? '--observation' : ''
                            sh """
                                mkdir -p test-results

                                smart-tests record session \\
                                    --build ${BUILD_TAG} \\
                                    --test-suite critical-tag-demo \\
                                    ${obsFlag} \\
                                    > session.txt

                                echo "Session: \$(cat session.txt) | Observation: ${params.SMART_TESTS_OBSERVATION} | Workspace: ${params.WORKSPACE_TARGET}"

                                if [ "${params.SMART_TESTS_OBSERVATION}" = "true" ]; then
                                    PYTHONPATH=. pytest tests/ --collect-only -q \\
                                        | grep '::' \\
                                        | smart-tests subset pytest --session @session.txt \\
                                        > subset.txt
                                else
                                    PYTHONPATH=. pytest tests/ --collect-only -q \\
                                        | grep '::' \\
                                        | smart-tests --log-level audit subset pytest \\
                                            --session @session.txt \\
                                            --${params.SUBSET_MODE} ${params.SUBSET_VALUE} \\
                                            --prioritized-tests-mapping smart-tests-mapping.json \\
                                            > subset.txt 2> subset_stderr.log
                                    echo "=== audit log ==="
                                    cat subset_stderr.log

                                    echo "=== COMPARISON: same --${params.SUBSET_MODE} ${params.SUBSET_VALUE}, NO mapping ==="
                                    PYTHONPATH=. pytest tests/ --collect-only -q \\
                                        | grep '::' \\
                                        | smart-tests subset pytest \\
                                            --session @session.txt \\
                                            --${params.SUBSET_MODE} ${params.SUBSET_VALUE} \\
                                        > subset_no_mapping.txt
                                    echo "=== NO MAPPING: selected \$(wc -l < subset_no_mapping.txt) / 16 tests ==="
                                    cat subset_no_mapping.txt

                                    echo "=== COMPARISON: --goal-spec combined syntax (prioritizeByTestMapping + select timePercentage=6%) ==="
                                    PYTHONPATH=. pytest tests/ --collect-only -q \\
                                        | grep '::' \\
                                        | smart-tests --log-level audit subset pytest \\
                                            --session @session.txt \\
                                            --goal-spec "prioritizeByTestMapping(),select(timePercentage=6%)" \\
                                            --prioritized-tests-mapping smart-tests-mapping.json \\
                                            > subset_goalspec.txt 2> subset_goalspec_stderr.log
                                    echo "=== GOAL-SPEC: selected \$(wc -l < subset_goalspec.txt) / 16 tests ==="
                                    cat subset_goalspec.txt
                                    echo "=== goal-spec audit log ==="
                                    cat subset_goalspec_stderr.log
                                    echo "=== goal-spec critical-test check ==="
                                    while IFS= read -r c; do
                                        grep -qF "\$c" subset_goalspec.txt && echo "goalspec present: \$c" || echo "goalspec MISSING: \$c"
                                    done < critical-node-ids.txt
                                fi

                                echo "=== Selected \$(wc -l < subset.txt) / 16 tests ==="
                                cat subset.txt

                                echo "=== Critical-test check ==="
                                while IFS= read -r c; do
                                    grep -qF "\$c" subset.txt && echo "present: \$c" || echo "MISSING: \$c"
                                done < critical-node-ids.txt

                                set --
                                while IFS= read -r line; do set -- "\$@" "\$line"; done < subset.txt
                                PYTHONPATH=. pytest "\$@" --junitxml=test-results/results.xml -v
                            """
                        }
                    }
                }
            }
            post {
                always {
                    container('python') {
                        withCredentials([string(credentialsId: "smart-tests-token-${params.WORKSPACE_TARGET}", variable: 'SMART_TESTS_TOKEN')]) {
                            sh 'smart-tests record tests pytest --session @session.txt test-results/results.xml || true'
                        }
                    }
                    junit 'test-results/results.xml'
                }
            }
        }
    }
}
