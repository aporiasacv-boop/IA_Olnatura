class ConfidenceEngine:

    def analytics_level(self, records_analyzed: int) -> str:
        if records_analyzed >= 100:
            return 'HIGH'
        if records_analyzed >= 50:
            return 'MEDIUM'
        return 'LOW'

    def document_level(self, average_score: float, total_matches: int) -> str:
        if total_matches == 0:
            return 'LOW'
        if average_score >= 0.80:
            return 'HIGH'
        if average_score >= 0.60:
            return 'MEDIUM'
        return 'LOW'

    def hybrid_level(self, analytics_level: str, document_level: str) -> str:
        levels = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
        combined = min(levels.get(analytics_level, 0), levels.get(document_level, 0))
        if combined >= 2:
            return 'HIGH'
        if combined >= 1:
            return 'MEDIUM'
        return 'LOW'

    def memory_level(self, snapshot_count: int) -> str:
        if snapshot_count >= 2:
            return 'HIGH'
        if snapshot_count == 1:
            return 'MEDIUM'
        return 'LOW'

    def copilot_level(self, analytics_level: str, document_level: str) -> str:
        return self.hybrid_level(analytics_level, document_level)
