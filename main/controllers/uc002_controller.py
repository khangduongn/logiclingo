from django.shortcuts import get_object_or_404
from ..models import Topic, Roadmap

class UC002Controller:
    def __init__(self):
        pass

    def read_roadmap(self, roadmap_id):
        """Read roadmap metadata including topics and exercises"""
        roadmap = get_object_or_404(Roadmap, roadmapID=roadmap_id)
        return {
            'roadmapID': roadmap.roadmapID,
            'topicIDs': [topic.topicID for topic in roadmap.topics.all()],
            'exerciseIDs': [exercise.exerciseID for topic in roadmap.topics.all() 
                          for exercise in topic.exercises.all()],
            'questionIDs': [question.questionID for topic in roadmap.topics.all() 
                          for exercise in topic.exercises.all() 
                          for question in exercise.questions.all()]
        }

    def modify_topic(self, topic_id):
        """Begin topic editing by reading topic data"""
        topic = get_object_or_404(Topic, topicID=topic_id)
        return {
            'topicID': topic.topicID,
            'topicName': topic.topicName,
            'topicDescription': topic.topicDescription,
            'topicNote': topic.topicNote
        }

    def validate_topic_input(self, topic_id, topic_name, topic_description, topic_note):
        """Validate topic input data"""
        if not topic_name or len(topic_name.strip()) == 0:
            return False, "Topic name cannot be empty"
        if not topic_description or len(topic_description.strip()) == 0:
            return False, "Topic description cannot be empty"
        if len(topic_name) > 100:
            return False, "Topic name is too long"
        if len(topic_description) > 500:
            return False, "Topic description is too long"
        if topic_note and len(topic_note) > 1000:
            return False, "Topic note is too long"
        return True, None

    def edit_topic_fields(self, topic_id, topic_name, topic_description, topic_note):
        """Update topic content"""
        topic = get_object_or_404(Topic, topicID=topic_id)
        topic.topicName = topic_name
        topic.topicDescription = topic_description
        topic.topicNote = topic_note
        topic.save()
        return topic

    def delete_topic(self, topic_id):
        """Remove topic permanently"""
        topic = get_object_or_404(Topic, topicID=topic_id)
        topic.delete()
        return True 