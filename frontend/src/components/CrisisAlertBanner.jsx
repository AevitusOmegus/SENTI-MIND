import { Phone, MessageCircle, ExternalLink, Heart } from "lucide-react";

const CRISIS_RESOURCES = [
  {
    name: "Umang Helpline (Pakistan)",
    phone: "0317-4288665",
    description: "Free mental health support, Mon–Sat 12–8pm",
    icon: Phone,
    color: "bg-medical-emergency",
    action: "Call Now",
  },
  {
    name: "Rozan Counseling (Pakistan)",
    phone: "051-2890505",
    description: "Counseling & crisis intervention, Islamabad",
    icon: Phone,
    color: "bg-sage-600",
    action: "Call Now",
  },
  {
    name: "International Crisis Text",
    phone: "741741",
    description: "Crisis Text Line — text HELLO for global support",
    icon: MessageCircle,
    color: "bg-indigo-600",
    action: "Text HELLO",
    href: "sms:741741?&body=HELLO",
  },
];

export default function CrisisAlertBanner({
  isVisible = false,
  category = "",
  confidence = 0,
}) {
  if (!isVisible) return null;

  return (
    <div 
      className="w-full animate-medical-fade-in"
      role="alert"
      aria-live="assertive"
    >
      <div className="bg-gradient-to-r from-medical-emergency to-rose-600 text-white p-6 rounded-2xl shadow-medical-lg">
        <div className="flex items-start gap-4">
          {/* Alert Icon */}
          <div className="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center flex-shrink-0 backdrop-blur-sm">
            <Heart className="w-7 h-7 animate-pulse" />
          </div>

          <div className="flex-1 min-w-0">
            {/* Header */}
            <h2 className="text-xl font-bold mb-2 flex items-center gap-2">
              We're Here to Help
            </h2>
            
            <p className="text-rose-100 text-sm leading-relaxed mb-5">
              Our analysis indicates you may be experiencing {category.toLowerCase()} symptoms
              with {(confidence * 100).toFixed(0)}% confidence. Your safety is our priority.
              Please reach out to one of these confidential resources:
            </p>

            {/* Crisis Resources Grid */}
            <div className="grid gap-3 sm:grid-cols-2">
              {CRISIS_RESOURCES.map((resource) => {
                const Icon = resource.icon;
                return (
                  <a
                    key={resource.name}
                    href={resource.href ?? `tel:${resource.phone}`}
                    className="flex items-center gap-3 p-4 rounded-xl bg-white/10 hover:bg-white/20 transition-all group border border-white/10"
                  >
                    <div
                      className={`w-11 h-11 rounded-xl ${resource.color} flex items-center justify-center flex-shrink-0 shadow-lg`}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm truncate">{resource.name}</p>
                      <p className="text-rose-100 text-xs opacity-90">{resource.description}</p>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-bold block">{resource.phone}</span>
                      <span className="text-xs opacity-75">{resource.action}</span>
                    </div>
                  </a>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-5 pt-5 border-t border-white/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <p className="text-sm text-rose-100 flex items-center gap-2">
            <span className="text-lg">💚</span>
            You are not alone. Help is available — completely free and confidential.
          </p>
          <a
            href="https://www.iamwhole.pk"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-white font-medium flex items-center gap-1.5 hover:underline whitespace-nowrap px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
          >
            More Resources
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Medical Disclaimer */}
      <div className="mt-3 p-3 bg-rose-50 rounded-xl border border-rose-200">
        <p className="text-xs text-rose-700 text-center">
          ⚠️ If you're in immediate danger, please call <strong className="font-semibold">115 (Rescue)</strong> or go to your nearest emergency room.
        </p>
      </div>
    </div>
  );
}
