targetScope = 'resourceGroup'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Container App name')
param containerAppName string = 'ca-google-adk-agents-poc'

@description('Container App environment name')
param containerAppEnvName string = 'cae-adk-poc'

@description('Azure Container Registry name (global unique)')
param acrName string

@description('Azure Key Vault name (global unique)')
param keyVaultName string

@description('User Assigned Managed Identity name')
param managedIdentityName string = 'uai-adk-poc'

@description('Container image name in ACR')
param imageName string = 'google-adk-agents-poc'

@description('Container image tag')
param imageTag string = 'latest'

@description('Target port exposed by the app')
param targetPort int = 8080

@description('OpenAI API key value')
@secure()
param openAiApiKey string

@description('Claude API key value')
@secure()
param claudeApiKey string

@description('Google API key value (only if not using Vertex)')
@secure()
param googleApiKey string = ''

@description('Enable Vertex AI mode in app')
param useVertexAi bool = false

@description('GCP Project ID used for Vertex AI mode')
param gcpProjectId string = ''

@description('GCP location used for Vertex AI mode')
param gcpLocation string = 'us-central1'

var acrLoginServer = '${acrName}.azurecr.io'
var imageRef = '${acrLoginServer}/${imageName}:${imageTag}'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
  }
}

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    sku: {
      name: 'standard'
      family: 'A'
    }
    enableRbacAuthorization: true
    enabledForTemplateDeployment: true
    publicNetworkAccess: 'Enabled'
  }
}

resource openAiSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'OPENAI-API-KEY'
  properties: {
    value: openAiApiKey
  }
}

resource claudeSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'CLAUDE-API-KEY'
  properties: {
    value: claudeApiKey
  }
}

resource googleSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'GOOGLE-API-KEY'
  properties: {
    value: googleApiKey
  }
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
}

resource containerAppEnv 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: containerAppEnvName
  location: location
  properties: {}
}

resource acrPullRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, managedIdentity.id, 'AcrPull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource kvSecretsUserRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, managedIdentity.id, 'KeyVaultSecretsUser')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: managedIdentity.id
        }
      ]
      secrets: [
        {
          name: 'openai-key'
          keyVaultUrl: openAiSecret.properties.secretUri
          identity: managedIdentity.id
        }
        {
          name: 'claude-key'
          keyVaultUrl: claudeSecret.properties.secretUri
          identity: managedIdentity.id
        }
        {
          name: 'google-key'
          keyVaultUrl: googleSecret.properties.secretUri
          identity: managedIdentity.id
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: imageRef
          env: [
            {
              name: 'OPENAI_API_KEY'
              secretRef: 'openai-key'
            }
            {
              name: 'CLAUDE_API_KEY'
              secretRef: 'claude-key'
            }
            {
              name: 'GOOGLE_API_KEY'
              secretRef: 'google-key'
            }
            {
              name: 'USE_VERTEX_AI'
              value: string(useVertexAi)
            }
            {
              name: 'PORT'
              value: string(targetPort)
            }
            {
              name: 'ADAPTER_SERVER_URL'
              value: 'http://127.0.0.1:${targetPort}'
            }
            {
              name: 'GOOGLE_CLOUD_PROJECT'
              value: gcpProjectId
            }
            {
              name: 'GOOGLE_CLOUD_LOCATION'
              value: gcpLocation
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
      }
    }
  }
  dependsOn: [
    acrPullRole
    kvSecretsUserRole
  ]
}

output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
output acrLoginServer string = acrLoginServer
output managedIdentityPrincipalId string = managedIdentity.properties.principalId
