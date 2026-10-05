{{- define "insighthub.labels" -}}
app.kubernetes.io/name: insighthub
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
