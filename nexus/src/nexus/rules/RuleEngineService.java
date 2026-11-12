package nexus.rules;

import nexus.common.EventBus;
import nexus.common.NexusEvent;
import nexus.common.NexusListener;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;

public class RuleEngineService implements NexusListener {
    
    public static class Rule {
        private String triggerEventType;
        private Consumer<NexusEvent> action;

        public Rule(String triggerEventType, Consumer<NexusEvent> action) {
            this.triggerEventType = triggerEventType;
            this.action = action;
        }

        public boolean matches(NexusEvent event) {
            return triggerEventType.equals(event.getType());
        }

        public void execute(NexusEvent event) {
            action.accept(event);
        }
    }

    private List<Rule> rules;

    public RuleEngineService() {
        rules = new ArrayList<>();
        EventBus.getInstance().subscribeToAll(this);
    }

    public void addRule(String triggerType, Consumer<NexusEvent> action) {
        rules.add(new Rule(triggerType, action));
    }

    @Override
    public void onEvent(NexusEvent event) {
        for (Rule r : rules) {
            if (r.matches(event)) {
                r.execute(event);
            }
        }
    }
}
