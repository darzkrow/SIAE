import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const StatCard = ({ icon, title, value, trend, trendLabel, color }) => {
    const IconComponent = icon;
    const trendColor = trend === 'up' ? 'text-green-500' : 'text-red-500';
    const trendIcon = trend === 'up' ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />;

    return (
        <div className="bg-white p-4 rounded-lg shadow-md flex items-center">
            <div className={`p-3 rounded-full mr-4 ${color}`}>
                <IconComponent className="h-6 w-6 text-white" />
            </div>
            <div>
                <p className="text-sm text-gray-500 font-medium">{title}</p>
                <p className="text-2xl font-bold text-gray-800">{value}</p>
                {trend && (
                    <div className="flex items-center text-xs text-gray-500 mt-1">
                        <span className={`flex items-center mr-1 ${trendColor}`}>
                            {trendIcon}
                            {trend}
                        </span>
                        <span>{trendLabel}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default StatCard;
