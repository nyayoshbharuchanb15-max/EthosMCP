{{- define "ai-compliance-mcp.fullname" -}}
{{- printf "%s-%s" .Release.Name "ai-compliance" | trunc 63 | trimSuffix "-" -}}
{{- end -}}
