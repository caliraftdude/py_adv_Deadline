# 7_code_translation/src/deadline/world/evidence_manager.py
"""
Evidence management system - tracks evidence collection and case solving
"""

from typing import Dict, List, Set, Optional, Any
import logging

logger = logging.getLogger(__name__)

class EvidenceManager:
    """Manages evidence collection and case solving"""
    
    def __init__(self):
        self.collected_evidence: Set[str] = set()
        self.evidence_values: Dict[str, int] = {}
        self.evidence_descriptions: Dict[str, str] = {}
        
        # Case solving
        self.accusation_made: bool = False
        self.accused_person: Optional[str] = None
        self.case_solved: bool = False
        
        # Solution data
        self.solution: Dict[str, Any] = {}
        
    def initialize(self, solution_data: Dict[str, Any]):
        """Initialize with solution data"""
        self.solution = solution_data
        
    def collect_evidence(self, evidence_id: str) -> bool:
        """
        Collect a piece of evidence
        Returns True if newly collected
        """
        if evidence_id not in self.collected_evidence:
            self.collected_evidence.add(evidence_id)
            logger.info(f"Evidence collected: {evidence_id}")
            return True
        return False
    
    def has_evidence(self, evidence_id: str) -> bool:
        """Check if evidence has been collected"""
        return evidence_id in self.collected_evidence
    
    def get_evidence_count(self) -> int:
        """Get total number of evidence pieces collected"""
        return len(self.collected_evidence)
    
    def get_evidence_value(self) -> int:
        """Calculate total value of collected evidence"""
        total = 0
        for evidence_id in self.collected_evidence:
            total += self.evidence_values.get(evidence_id, 0)
        return total
    
    def has_sufficient_evidence(self) -> bool:
        """Check if player has enough evidence to solve the case"""
        required = set(self.solution.get('required_evidence', []))
        return required.issubset(self.collected_evidence)
    
    def make_accusation(self, person: str) -> tuple[bool, str]:
        """
        Make an accusation against someone
        Returns (success, message)
        """
        self.accusation_made = True
        self.accused_person = person
        
        correct_murderer = self.solution.get('murderer')
        
        if person == correct_murderer:
            if self.has_sufficient_evidence():
                self.case_solved = True
                return True, f"Congratulations! You've correctly identified {person} as the murderer with sufficient evidence."
            else:
                return False, f"You've identified the right person, but you don't have enough evidence to convict."
        else:
            return False, f"Your accusation against {person} is incorrect. The case remains unsolved."
    
    def check_confession_trigger(self, person: str) -> bool:
        """Check if conditions are met for a confession"""
        trigger = self.solution.get('confession_trigger', {})
        
        # Check evidence count
        if len(self.collected_evidence) < trigger.get('evidence_count', 999):
            return False
        
        # Check specific items
        required_items = set(trigger.get('specific_items', []))
        if not required_items.issubset(self.collected_evidence):
            return False
        
        # Check trust level (would need character manager for this)
        # For now, return True if other conditions are met
        return True
    
    def get_evidence_summary(self) -> List[str]:
        """Get a summary of collected evidence"""
        summary = []
        for evidence_id in sorted(self.collected_evidence):
            desc = self.evidence_descriptions.get(evidence_id, evidence_id)
            summary.append(f"- {desc}")
        return summary
    
    def is_case_solved(self) -> bool:
        """Check if the case has been solved"""
        return self.case_solved