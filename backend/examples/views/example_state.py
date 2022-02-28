from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from examples.models import Example, ExampleState
from examples.serializers import ExampleStateSerializer
from projects.models import Project
from projects.permissions import IsProjectMember


class ExampleStateList(generics.ListCreateAPIView):
    serializer_class = ExampleStateSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    @property
    def can_confirm_per_user(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return not project.collaborative_annotation

    def get_queryset(self):
        queryset = ExampleState.objects.filter(example=self.kwargs["example_id"])
        if self.can_confirm_per_user:
            queryset = queryset.filter(confirmed_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        queryset = self.get_queryset()
        example_id = self.kwargs['example_id']
        example = Example.objects.get(pk=example_id)

        if queryset.exists():
            example.annotations_approved_by = None
            example.save()
            queryset.delete()
        else:
            example = get_object_or_404(Example, pk=self.kwargs["example_id"])
            example.annotations_approved_by = self.request.user
            example.save()
            serializer.save(example=example, confirmed_by=self.request.user)
